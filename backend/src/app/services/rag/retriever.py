"""
Lightweight RAG retriever for agricultural safety guidelines.

Strategy: No external vector DB required. Uses TF-IDF cosine similarity
over a curated knowledge base of pesticide safety rules, loaded once at startup.
This injects verified chemical constraints into the LLM system prompt so
recommendations never suggest banned or incorrect products.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import NamedTuple


class KnowledgeChunk(NamedTuple):
    id: str
    disease: str
    content: str
    keywords: list[str]


# ──────────────────────────────────────────────────────────────
# Curated Agronomic Knowledge Base
# Based on Indian agricultural guidelines (ICAR / Central Insecticide Board)
# Covering all 5 supported crops: Cotton, Groundnut, Pepper Bell, Potato, Tomato
# ──────────────────────────────────────────────────────────────
KNOWLEDGE_BASE: list[KnowledgeChunk] = [
    KnowledgeChunk(
        id="cotton_bollworm",
        disease="Cotton Bollworm",
        content=(
            "For Cotton Bollworm (Helicoverpa armigera / Pectinophora gossypiella), recommended insecticides are "
            "Chlorpyrifos 20EC (2ml/L), Indoxacarb 14.5SC (1ml/L), or Spinosad 45SC (0.3ml/L). Avoid Endosulfan — "
            "it is BANNED in India. Spray during early morning or late evening. Maintain a 14-day pre-harvest interval (PHI)."
        ),
        keywords=["cotton", "bollworm", "helicoverpa", "spinosad", "indoxacarb", "chlorpyrifos", "pink bollworm"],
    ),
    KnowledgeChunk(
        id="cotton_leaf_curl",
        disease="Cotton Leaf Curl & Bacterial Blight",
        content=(
            "For Cotton Leaf Curl Virus transmitted by whiteflies, manage vectors with Diafenthiuron 50WP (1.2g/L) "
            "or Neem oil 1500ppm (3ml/L). For Bacterial Blight (Xanthomonas), spray Copper Oxychloride 50WP (2.5g/L) "
            "mixed with Streptocycline (100mg/L). Never spray Monocrotophos."
        ),
        keywords=["cotton", "leaf curl", "whitefly", "bacterial blight", "xanthomonas", "copper oxychloride", "streptocycline"],
    ),
    KnowledgeChunk(
        id="tomato_blight",
        disease="Tomato Early and Late Blight",
        content=(
            "For Tomato Early Blight (Alternaria solani), apply Mancozeb 75WP (2g/L) or Chlorothalonil 75WP (2g/L). "
            "For Late Blight (Phytophthora infestans), apply Metalaxyl 8% + Mancozeb 64% (2.5g/L) or Cymoxanil + Mancozeb. "
            "Copper Oxychloride (3g/L) is permitted for organic use. PHI for Mancozeb on tomato is 5 days."
        ),
        keywords=["tomato", "early blight", "late blight", "alternaria", "phytophthora", "mancozeb", "metalaxyl", "copper"],
    ),
    KnowledgeChunk(
        id="potato_blight",
        disease="Potato Late Blight & Early Blight",
        content=(
            "For Potato Late Blight (Phytophthora infestans), apply prophylactic spray of Mancozeb 75WP (2.5g/L). "
            "Under active infection, apply Cymoxanil 8% + Mancozeb 64% (2.5g/L) or Fenamidone + Mancozeb. "
            "Avoid excessive irrigation during fog/high humidity. Observe 14-day PHI before tuber harvest."
        ),
        keywords=["potato", "late blight", "early blight", "phytophthora", "cymoxanil", "mancozeb", "tuber"],
    ),
    KnowledgeChunk(
        id="pepper_bell_anthracnose",
        disease="Pepper Bell Anthracnose & Bacterial Spot",
        content=(
            "For Pepper Bell / Capsicum Anthracnose (Colletotrichum), spray Azoxystrobin 23SC (1ml/L) or "
            "Difenoconazole 25EC (1ml/L). For Bacterial Spot (Xanthomonas), apply Copper Hydroxide (2g/L). "
            "Allow 7-day PHI before picking bell peppers. Avoid overhead sprinkler irrigation."
        ),
        keywords=["pepper", "bell", "capsicum", "anthracnose", "colletotrichum", "azoxystrobin", "difenoconazole", "bacterial spot"],
    ),
    KnowledgeChunk(
        id="groundnut_tikka",
        disease="Groundnut Tikka Leaf Spot & Rust",
        content=(
            "For Groundnut Tikka / Leaf Spot (Cercospora arachidicola) and Rust (Puccinia arachidis), apply "
            "Hexaconazole 5EC (2ml/L) or Chlorothalonil 75WP (2g/L) or Mancozeb 75WP (2g/L). "
            "Carbendazim 50WP (1g/L) is effective if alternate sprays are used. PHI is 14 days."
        ),
        keywords=["groundnut", "peanut", "tikka", "leaf spot", "cercospora", "rust", "hexaconazole", "chlorothalonil"],
    ),
    KnowledgeChunk(
        id="general_pesticide_safety",
        disease="General Pesticide Safety",
        content=(
            "BANNED pesticides in India: Endosulfan, Monocrotophos, Methyl Parathion, Phorate (certain crops), Carbaryl. "
            "Always advise personal protective equipment (PPE): gloves, eye goggles, face mask. "
            "Observe Pre-Harvest Interval (PHI). Protect pollinator bees: do not spray during midday flowering; spray before 6AM or after 6PM."
        ),
        keywords=["banned", "safety", "ppe", "organic", "endosulfan", "monocrotophos", "bee", "general", "phi"],
    ),
]


# ──────────────────────────────────────────────────────────────
# TF-IDF Cosine Similarity Retriever (no external dependencies)
# ──────────────────────────────────────────────────────────────
def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z]{2,}\b", text.lower())


def _tf(tokens: list[str]) -> dict[str, float]:
    counts = Counter(tokens)
    total = len(tokens) or 1
    return {word: count / total for word, count in counts.items()}


def _idf(word: str, corpus_tokens: list[list[str]]) -> float:
    doc_count = sum(1 for tokens in corpus_tokens if word in tokens)
    return math.log((len(corpus_tokens) + 1) / (doc_count + 1)) + 1


def _cosine(vec_a: dict, vec_b: dict) -> float:
    common = set(vec_a) & set(vec_b)
    dot = sum(vec_a[w] * vec_b[w] for w in common)
    mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values())) or 1
    mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values())) or 1
    return dot / (mag_a * mag_b)


# Pre-compute corpus tokens once at import time
_CORPUS_TOKENS = [_tokenize(c.content + " " + " ".join(c.keywords)) for c in KNOWLEDGE_BASE]
_IDF_CACHE: dict[str, float] = {}


def _tfidf_vector(tokens: list[str]) -> dict[str, float]:
    tf = _tf(tokens)
    return {
        word: tf_val * _IDF_CACHE.setdefault(word, _idf(word, _CORPUS_TOKENS))
        for word, tf_val in tf.items()
    }


def retrieve_context_with_ids(query: str, top_k: int = 2) -> tuple[str, list[str]]:
    """
    Retrieve formatted context text alongside matching chunk IDs for audit logging.
    """
    query_tokens = _tokenize(query)
    query_vec = _tfidf_vector(query_tokens)

    scored: list[tuple[float, KnowledgeChunk]] = []
    for idx, chunk in enumerate(KNOWLEDGE_BASE):
        chunk_vec = _tfidf_vector(_CORPUS_TOKENS[idx])
        score = _cosine(query_vec, chunk_vec)
        scored.append((score, chunk))

    results = sorted(scored, key=lambda x: x[0], reverse=True)[:top_k]
    safety_chunk = next((c for c in KNOWLEDGE_BASE if c.id == "general_pesticide_safety"), None)

    chunks_to_return = [r[1] for r in results if r[0] > 0.04]
    if safety_chunk and safety_chunk not in chunks_to_return:
        chunks_to_return.append(safety_chunk)

    if not chunks_to_return:
        return "", []

    chunk_ids = [c.id for c in chunks_to_return]
    sections = "\n\n".join(f"[{c.disease}]\n{c.content}" for c in chunks_to_return)
    context_text = (
        "=== VERIFIED AGRONOMIC SAFETY GUIDELINES (use these constraints when making recommendations) ===\n"
        + sections
        + "\n=== END OF GUIDELINES ==="
    )
    return context_text, chunk_ids


def retrieve_context(query: str, top_k: int = 2) -> str:
    """Backward-compatible context retriever."""
    text, _ = retrieve_context_with_ids(query, top_k=top_k)
    return text


