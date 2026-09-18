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
    disease: str
    content: str
    keywords: list[str]


# ──────────────────────────────────────────────────────────────
# Curated Agronomic Knowledge Base
# Based on Indian agricultural guidelines (ICAR / Central Insecticide Board)
# ──────────────────────────────────────────────────────────────
KNOWLEDGE_BASE: list[KnowledgeChunk] = [
    KnowledgeChunk(
        disease="Cotton Bollworm",
        content=(
            "For Cotton Bollworm (Helicoverpa armigera), recommended pesticides are Chlorpyrifos 20EC "
            "(2ml/L) or Indoxacarb 14.5SC (1ml/L). Avoid Endosulfan — it is BANNED in India under the "
            "Insecticides Act. Spray during early morning or evening only. Maintain a 14-day pre-harvest "
            "interval (PHI). Do NOT spray within 500m of water bodies."
        ),
        keywords=["cotton", "bollworm", "helicoverpa", "chlorpyrifos", "indoxacarb", "pink bollworm"],
    ),
    KnowledgeChunk(
        disease="Tomato Early Blight",
        content=(
            "For Tomato Early Blight (Alternaria solani), apply Mancozeb 75WP (2g/L) or Chlorothalonil 75WP (2g/L). "
            "Copper Oxychloride (3g/L) is also effective and permitted for organic farming. "
            "Avoid Captan on food crops within 7 days of harvest. Rotate fungicides every 2 sprays to prevent resistance. "
            "Do NOT mix Mancozeb with alkaline pesticides."
        ),
        keywords=["tomato", "early blight", "alternaria", "mancozeb", "chlorothalonil", "copper"],
    ),
    KnowledgeChunk(
        disease="Rice Blast",
        content=(
            "For Rice Blast (Pyricularia oryzae), Tricyclazole 75WP (0.6g/L) is the first-choice systemic fungicide. "
            "Propiconazole 25EC (1ml/L) is an alternative. PHI is 15 days. "
            "Do NOT apply during flowering stage. Kasugamycin (2g/L) is recommended as an antibiotic alternative "
            "if systemic resistance is suspected. Avoid repeated use of the same active ingredient."
        ),
        keywords=["rice", "blast", "pyricularia", "tricyclazole", "propiconazole", "kasugamycin"],
    ),
    KnowledgeChunk(
        disease="Wheat Rust",
        content=(
            "For Wheat Yellow Rust (Puccinia striiformis) or Brown Rust (P. recondita), apply Propiconazole 25EC "
            "(1ml/L) at early infection. Tebuconazole 25.9EC (1ml/L) is effective for heavy infections. "
            "PHI is 35 days. Do NOT apply more than 2 fungicide sprays per season to prevent resistance buildup."
        ),
        keywords=["wheat", "rust", "yellow rust", "brown rust", "puccinia", "propiconazole", "tebuconazole"],
    ),
    KnowledgeChunk(
        disease="Groundnut Leaf Spot",
        content=(
            "For Groundnut Tikka / Leaf Spot (Cercospora arachidicola), apply Chlorothalonil 75WP (2g/L) "
            "or Mancozeb 75WP (2.5g/L) at 10-day intervals. Carbendazim 50WP (1g/L) is an effective systemic option. "
            "PHI for Mancozeb is 10 days. Avoid spraying after pod formation to prevent contamination."
        ),
        keywords=["groundnut", "peanut", "leaf spot", "tikka", "cercospora", "chlorothalonil", "carbendazim"],
    ),
    KnowledgeChunk(
        disease="General Pesticide Safety",
        content=(
            "BANNED pesticides in India (not to recommend under any circumstances): Endosulfan, Monocrotophos, "
            "Methyl Parathion, Phorate (on certain crops), Carbaryl (on some uses). "
            "Always recommend PPE: gloves, mask, goggles. Never recommend aerial spraying near schools or hospitals. "
            "Bee-safe window: spray only after 6PM or before 6AM when pollinators are inactive. "
            "Organic certified farms must use only copper, sulfur, neem-based, or Bacillus thuringiensis (Bt) products."
        ),
        keywords=["banned", "safety", "ppe", "organic", "endosulfan", "monocrotophos", "bee", "general"],
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


def retrieve_context(query: str, top_k: int = 2) -> str:
    """
    Retrieve the most relevant knowledge chunks for a given disease/crop query.
    Returns a pre-formatted string ready to inject into an LLM system prompt.

    Args:
        query: The disease label + crop label from the AI pipeline (e.g. "Cotton Bollworm")
        top_k: Number of chunks to retrieve

    Returns:
        A formatted context string or empty string if nothing relevant found.
    """
    query_tokens = _tokenize(query)
    query_vec = _tfidf_vector(query_tokens)

    scored: list[tuple[float, KnowledgeChunk]] = []
    for idx, chunk in enumerate(KNOWLEDGE_BASE):
        chunk_vec = _tfidf_vector(_CORPUS_TOKENS[idx])
        score = _cosine(query_vec, chunk_vec)
        scored.append((score, chunk))

    # Always include the general safety chunk
    results = sorted(scored, key=lambda x: x[0], reverse=True)[:top_k]
    safety_chunk = next((c for c in KNOWLEDGE_BASE if c.disease == "General Pesticide Safety"), None)

    chunks_to_return = [r[1] for r in results if r[0] > 0.05]
    if safety_chunk and safety_chunk not in chunks_to_return:
        chunks_to_return.append(safety_chunk)

    if not chunks_to_return:
        return ""

    sections = "\n\n".join(f"[{c.disease}]\n{c.content}" for c in chunks_to_return)
    return (
        "=== VERIFIED AGRONOMIC SAFETY GUIDELINES (use these constraints when making recommendations) ===\n"
        + sections
        + "\n=== END OF GUIDELINES ==="
    )

