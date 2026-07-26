from statistics import median

from sqlalchemy import select
from sqlalchemy.orm import Session

from clipops.models import (
    AccountProfile,
    ClipCandidate,
    PerformanceRecord,
    PublishingQueueItem,
)


def dashboard_metrics(session: Session) -> dict[str, object]:
    candidates = session.scalars(select(ClipCandidate)).all()
    queued = session.scalars(select(PublishingQueueItem)).all()
    records = session.execute(
        select(PerformanceRecord, PublishingQueueItem, AccountProfile)
        .join(PublishingQueueItem, PublishingQueueItem.id == PerformanceRecord.queue_item_id)
        .join(AccountProfile, AccountProfile.id == PublishingQueueItem.account_profile_id)
    ).all()
    accounts = []
    for account in session.scalars(select(AccountProfile)).all():
        account_records = [record for record, item, profile in records if profile.id == account.id]
        engagement = median([record.engagement_rate for record in account_records]) if account_records else 0
        accounts.append({"account": account.name, "published_clips": len(account_records), "median_engagement_rate": engagement, "health_score": min(100, round(engagement * 500))})
    approved = sum(candidate.status in {"APPROVED", "READY_TO_PUBLISH", "PUBLISHED"} for candidate in candidates)
    return {"simulated": True, "approval_rate": approved / len(candidates) if candidates else 0, "queue_status": len(queued), "accounts": accounts}
