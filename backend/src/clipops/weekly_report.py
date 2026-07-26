from __future__ import annotations

from collections import Counter
from datetime import UTC, date, datetime, timedelta
from statistics import median
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from clipops.metrics import dashboard_metrics
from clipops.model_provider import WeeklyRecommendationContext
from clipops.models import (
    AccountProfile,
    ClipCandidate,
    ClipScore,
    ContentExperiment,
    ModelRun,
    PerformanceRecord,
    PublishingQueueItem,
    WeeklyGrowthReport,
    WorkflowRun,
)

MAX_REPORT_CLIPS = 3


class WeeklyRecommendationProvider(Protocol):
    provider_name: str

    def draft_weekly_recommendation(self, context: WeeklyRecommendationContext) -> dict[str, str]: ...


def _clip_rows(session: Session) -> list[tuple[PerformanceRecord, PublishingQueueItem, ClipCandidate, AccountProfile, ClipScore | None]]:
    return session.execute(
        select(PerformanceRecord, PublishingQueueItem, ClipCandidate, AccountProfile, ClipScore)
        .join(PublishingQueueItem, PublishingQueueItem.id == PerformanceRecord.queue_item_id)
        .join(ClipCandidate, ClipCandidate.id == PublishingQueueItem.candidate_id)
        .join(AccountProfile, AccountProfile.id == PublishingQueueItem.account_profile_id)
        .outerjoin(ClipScore, ClipScore.candidate_id == ClipCandidate.id)
    ).all()


def _engagement_key(row: tuple[PerformanceRecord, PublishingQueueItem, ClipCandidate, AccountProfile, ClipScore | None]) -> tuple[float, int, int]:
    record, _, _, _, score = row
    return (record.engagement_rate, record.views, score.overall_score if score else 0)


def _clip_summary(
    row: tuple[PerformanceRecord, PublishingQueueItem, ClipCandidate, AccountProfile, ClipScore | None],
    *,
    issue: bool = False,
) -> dict[str, object]:
    record, _, candidate, account, score = row
    summary: dict[str, object] = {
        "candidate_id": candidate.id,
        "account": account.name,
        "platform": account.platform,
        "transcript_excerpt": candidate.transcript_excerpt,
        "views": record.views,
        "engagement_rate": record.engagement_rate,
        "overall_score": score.overall_score if score else None,
    }
    if issue:
        summary["likely_issue"] = "Lower simulated engagement than peer clips; review hook clarity, CTA match, and edit pacing."
    else:
        summary["why_it_worked"] = score.explanation if score else "Higher simulated engagement in the loaded demo records."
    return summary


def _experiment_readout(session: Session) -> dict[str, object]:
    experiment = session.scalars(select(ContentExperiment).order_by(ContentExperiment.id.desc())).first()
    if not experiment:
        return {
            "status": "missing",
            "summary": "No experiment has been recorded yet.",
            "winner": None,
            "confidence_note": "Create a hook, CTA, content-pillar, or duration experiment before treating this as a readout.",
        }
    return {
        "status": "available",
        "experiment_id": experiment.id,
        "name": experiment.name,
        "hypothesis": experiment.hypothesis,
        "primary_metric": experiment.primary_metric,
        "variant_a": experiment.variant_a,
        "variant_b": experiment.variant_b,
        "result_summary": experiment.result_summary or "No result summary recorded.",
        "winner": experiment.winner or "No winner recorded.",
        "confidence_note": experiment.confidence_note or "Directional only; no statistical significance claim.",
    }


def _workflow_metrics(session: Session, approval_rate: float, queued_count: int) -> dict[str, object]:
    runs = session.scalars(select(WorkflowRun)).all()
    model_runs = session.scalars(select(ModelRun)).all()
    status_counts = Counter(run.status for run in runs)
    successful_runs = status_counts.get("COMPLETED", 0)
    return {
        "workflow_runs": len(runs),
        "status_counts": dict(sorted(status_counts.items())),
        "success_rate": successful_runs / len(runs) if runs else 0,
        "model_runs": len(model_runs),
        "repair_attempts": sum(run.repair_count for run in model_runs),
        "approval_rate": approval_rate,
        "queued_clip_count": queued_count,
    }


def _content_backlog_suggestions(top_clips: list[dict[str, object]], experiment: dict[str, object]) -> list[str]:
    suggestions = [
        "Create one follow-up clip that expands the top-performing excerpt into a concrete tactic.",
        "Draft one safer variant with a lower-claim hook for human review.",
    ]
    if experiment.get("winner") and experiment["winner"] != "No winner recorded.":
        suggestions.append(f"Queue two new candidates using the current winning variant: {experiment['winner']}.")
    if not top_clips:
        suggestions.append("Generate and publish simulated demo candidates before ranking content backlog ideas.")
    return suggestions


def _next_experiment(
    experiment: dict[str, object],
    provider: WeeklyRecommendationProvider | None,
    context: WeeklyRecommendationContext,
) -> dict[str, object]:
    if provider:
        draft = provider.draft_weekly_recommendation(context)
        return {
            **draft,
            "recommendation_source": provider.provider_name,
        }

    winner = experiment.get("winner")
    winner_text = str(winner) if winner and winner != "No winner recorded." else "the clearest current hook"
    return {
        "name": "Next hook-style comparison",
        "hypothesis": f"{winner_text} will improve simulated engagement when paired with a more specific CTA.",
        "primary_metric": "engagement_rate",
        "variant_a": "Direct problem hook",
        "variant_b": "Curiosity hook",
        "rationale": "Deterministic recommendation based on the current experiment readout and fleet metrics.",
        "recommendation_source": "deterministic",
    }


def generate_weekly_report(
    session: Session,
    week_end: date | None = None,
    provider: WeeklyRecommendationProvider | None = None,
) -> WeeklyGrowthReport:
    week_end = week_end or datetime.now(UTC).date()
    week_start = week_end - timedelta(days=6)
    metrics = dashboard_metrics(session)
    accounts = session.scalars(select(AccountProfile).order_by(AccountProfile.name)).all()
    rows = _clip_rows(session)
    top_rows = sorted(rows, key=_engagement_key, reverse=True)[:MAX_REPORT_CLIPS]
    top_candidate_ids = {candidate.id for _, _, candidate, _, _ in top_rows}
    underperforming_rows = [
        row for row in sorted(rows, key=_engagement_key) if row[2].id not in top_candidate_ids
    ][:MAX_REPORT_CLIPS]
    if not underperforming_rows and len(rows) > 1:
        underperforming_rows = sorted(rows, key=_engagement_key)[:1]
    top_clips = [_clip_summary(row) for row in top_rows]
    underperforming_clips = [_clip_summary(row, issue=True) for row in underperforming_rows]
    experiment = _experiment_readout(session)
    workflow = _workflow_metrics(session, float(metrics["approval_rate"]), int(metrics["queue_status"]))
    engagement_values = [record.engagement_rate for record, *_ in rows]
    median_engagement = median(engagement_values) if engagement_values else 0
    fleet_snapshot = {
        "approval_rate": metrics["approval_rate"],
        "queued_clip_count": metrics["queue_status"],
        "published_clip_count": len(rows),
        "account_count": len(accounts),
        "median_simulated_engagement_rate": median_engagement,
        "account_health": metrics["accounts"],
    }
    accounts_covered = [
        {"account_id": account.id, "name": account.name, "platform": account.platform}
        for account in accounts
    ]
    context = WeeklyRecommendationContext(
        approval_rate=float(metrics["approval_rate"]),
        median_engagement_rate=median_engagement,
        experiment_winner=str(experiment.get("winner")) if experiment.get("winner") else None,
        top_clip_count=len(top_clips),
    )
    next_experiment = _next_experiment(experiment, provider, context)
    caveats = [
        "All performance records in this POC are simulated demo data.",
        "The report is directional and does not prove causality, forecast growth, or guarantee results.",
        "The current data model has limited event dates, so the report summarizes loaded records for the requested week range.",
    ]
    report = WeeklyGrowthReport(
        id=f"weekly:{week_end.isoformat()}",
        week_range=f"{week_start.isoformat()} to {week_end.isoformat()}",
        accounts_covered=accounts_covered,
        summary=(
            f"Simulated weekly snapshot: {metrics['approval_rate']:.0%} approval rate across "
            f"{len(accounts)} accounts and {len(rows)} published clips. "
            f"Experiment winner: {experiment.get('winner') or 'not available'}. "
            f"Next experiment: {next_experiment['name']}. Caveat: simulated, directional data only."
        ),
        fleet_snapshot=fleet_snapshot,
        top_clips=top_clips,
        underperforming_clips=underperforming_clips,
        experiment_readout=experiment,
        workflow_metrics=workflow,
        next_experiment=next_experiment,
        content_backlog_suggestions=_content_backlog_suggestions(top_clips, experiment),
        caveats=caveats,
        simulated=True,
    )
    report = session.merge(report)
    session.commit()
    session.refresh(report)
    return report
