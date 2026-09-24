"""
Backfill script to pre-translate and transliterate all existing dynamic content in the database.

Usage:
    # Direct processing (immediate DB updates via Google Translate/transliteration):
    python -m src.app.scripts.backfill_translations --direct

    # Enqueue as background jobs into Redis ARQ queue:
    python -m src.app.scripts.backfill_translations --queue

    # Re-process and retry failed translation attempts:
    python -m src.app.scripts.backfill_translations --retry-failed --direct

    # Filter to specific entity type:
    python -m src.app.scripts.backfill_translations --entity prediction --direct
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path if run directly as script
backend_root = Path(__file__).resolve().parent.parent.parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.core.session import _session_factory
from app.models import Prediction, ExpertReview, Alert, Farm, Plot, User
from app.models.translation import EntityTranslation
from app.services.translation.manager import process_entity_translation_sync
from app.core.arq import enqueue_translation, init_arq, close_arq

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("smart-farming.backfill")


def get_recommendation_fields(rec: dict) -> dict[str, str]:
    fields = {}
    valid_keys = [
        "immediate_action", "treatment", "prevention", "monitoring",
        "safety_disclaimer", "action", "fertilizer", "pesticide",
        "irrigation", "prevention_tips"
    ]
    for k in valid_keys:
        v = rec.get(k)
        if v and isinstance(v, str) and v.strip():
            fields[k] = v.strip()
    return fields


async def run_backfill(
    mode: str = "direct",
    entity_filter: str | None = None,
    retry_failed: bool = False,
    limit: int | None = None,
):
    session = _session_factory()()
    logger.info("Starting translation backfill (mode: %s, filter: %s)...", mode, entity_filter or "all")

    if mode == "queue":
        await init_arq()

    total_entities = 0
    total_fields = 0

    try:
        # 1. Predictions
        if not entity_filter or entity_filter == "prediction":
            logger.info("Scanning Predictions...")
            query = session.query(Prediction).order_by(Prediction.id.asc())
            if limit:
                query = query.limit(limit)
            preds = query.all()

            for p in preds:
                rec = (p.result or {}).get("recommendation", {})
                if rec and isinstance(rec, dict):
                    fields = get_recommendation_fields(rec)
                    if fields:
                        total_entities += 1
                        total_fields += len(fields)
                        if mode == "direct":
                            stats = process_entity_translation_sync(
                                session, "prediction", str(p.id), fields
                            )
                            logger.info("Prediction #%d translated: %s", p.id, stats)
                        else:
                            await enqueue_translation("prediction", str(p.id), fields)

        # 2. Expert Reviews
        if not entity_filter or entity_filter == "expert_review":
            logger.info("Scanning Expert Reviews...")
            query = session.query(ExpertReview).filter(
                ExpertReview.farmer_guidance.isnot(None),
                ExpertReview.farmer_guidance != "",
            )
            if limit:
                query = query.limit(limit)
            reviews = query.all()

            for r in reviews:
                total_entities += 1
                total_fields += 1
                fields = {"farmer_guidance": r.farmer_guidance}
                if mode == "direct":
                    stats = process_entity_translation_sync(
                        session, "expert_review", str(r.id), fields
                    )
                    logger.info("ExpertReview #%d translated: %s", r.id, stats)
                else:
                    await enqueue_translation("expert_review", str(r.id), fields)

        # 3. Alerts
        if not entity_filter or entity_filter == "alert":
            logger.info("Scanning Alerts...")
            query = session.query(Alert).filter(Alert.title.isnot(None))
            if limit:
                query = query.limit(limit)
            alerts = query.all()

            for a in alerts:
                fields = {}
                if a.title:
                    fields["title"] = a.title
                if a.body:
                    fields["body"] = a.body
                if fields:
                    total_entities += 1
                    total_fields += len(fields)
                    if mode == "direct":
                        stats = process_entity_translation_sync(
                            session, "alert", str(a.id), fields
                        )
                        logger.info("Alert #%d translated: %s", a.id, stats)
                    else:
                        await enqueue_translation("alert", str(a.id), fields)

        # 4. Farms
        if not entity_filter or entity_filter == "farm":
            logger.info("Scanning Farms...")
            query = session.query(Farm)
            if limit:
                query = query.limit(limit)
            farms = query.all()

            for f in farms:
                fields = {"name": f.name}
                if f.location:
                    fields["location"] = f.location
                total_entities += 1
                total_fields += len(fields)
                if mode == "direct":
                    stats = process_entity_translation_sync(
                        session, "farm", str(f.id), fields, name_fields=["name", "location"]
                    )
                    logger.info("Farm #%d transliterated: %s", f.id, stats)
                else:
                    await enqueue_translation(
                        "farm", str(f.id), fields, name_fields=["name", "location"]
                    )

        # 5. Plots
        if not entity_filter or entity_filter == "plot":
            logger.info("Scanning Plots...")
            query = session.query(Plot)
            if limit:
                query = query.limit(limit)
            plots = query.all()

            for pl in plots:
                fields = {"name": pl.name}
                total_entities += 1
                total_fields += 1
                if mode == "direct":
                    stats = process_entity_translation_sync(
                        session, "plot", str(pl.id), fields, name_fields=["name"]
                    )
                    logger.info("Plot #%d transliterated: %s", pl.id, stats)
                else:
                    await enqueue_translation(
                        "plot", str(pl.id), fields, name_fields=["name"]
                    )

        # 6. Users
        if not entity_filter or entity_filter == "user":
            logger.info("Scanning Users...")
            query = session.query(User)
            if limit:
                query = query.limit(limit)
            users = query.all()

            for u in users:
                fields = {"name": u.name}
                total_entities += 1
                total_fields += 1
                if mode == "direct":
                    stats = process_entity_translation_sync(
                        session, "user", str(u.id), fields, name_fields=["name"]
                    )
                    logger.info("User #%s transliterated: %s", u.id, stats)
                else:
                    await enqueue_translation(
                        "user", str(u.id), fields, name_fields=["name"]
                    )

        # 7. Retry Failed
        if retry_failed:
            logger.info("Scanning previously failed translations...")
            failed_records = session.query(EntityTranslation).filter_by(status="failed").all()
            logger.info("Found %d failed translations to retry", len(failed_records))
            for fr in failed_records:
                # Mark as pending to allow retry
                fr.status = "pending"
                session.commit()
                fields = {fr.field_name: fr.translated_text or ""}
                name_fields = [fr.field_name] if fr.is_transliteration else []
                if mode == "direct":
                    process_entity_translation_sync(
                        session, fr.entity_type, fr.entity_id, fields, name_fields
                    )
                else:
                    await enqueue_translation(
                        fr.entity_type, fr.entity_id, fields, name_fields
                    )

        logger.info(
            "Backfill completed successfully. Total entities processed: %d, total fields: %d",
            total_entities, total_fields
        )

    finally:
        session.close()
        if mode == "queue":
            await close_arq()


def main():
    parser = argparse.ArgumentParser(description="Smart Farming dynamic database translation backfill script.")
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Execute translations directly in this process and write immediately to DB.",
    )
    parser.add_argument(
        "--queue",
        action="store_true",
        help="Enqueue translation jobs into the Redis ARQ worker queue.",
    )
    parser.add_argument(
        "--entity",
        choices=["prediction", "expert_review", "alert", "farm", "plot", "user"],
        help="Filter to a specific entity type.",
    )
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Retry previously failed translations in entity_translations table.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max number of records per entity to process.",
    )
    args = parser.parse_args()

    mode = "queue" if args.queue else "direct"
    asyncio.run(
        run_backfill(
            mode=mode,
            entity_filter=args.entity,
            retry_failed=args.retry_failed,
            limit=args.limit,
        )
    )


if __name__ == "__main__":
    main()
