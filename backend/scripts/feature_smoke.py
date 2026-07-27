from __future__ import annotations

import argparse
import tempfile
import warnings
from pathlib import Path
from uuid import uuid4

warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated.*")

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from clipops.database import make_engine
from clipops.main import app
from clipops.models import Base, ClipCandidate, GeneratedAsset
from clipops.schemas import ClipScoreSchema
from clipops.scoring import save_score
from clipops.seed import seed
from clipops.srt_adapter import parse_srt
from clipops.workflow import run_workflow

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
SRT_FIXTURE = ROOT / "seed-data" / "demo-2min.srt"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def pass_line(name: str, detail: str) -> None:
    print(f"[PASS] {name}: {detail}")


def score_input(index: int) -> ClipScoreSchema:
    rows = [
        (5, 4, 3, 4, 3, 5, 5, 2, 0.80),
        (4, 4, 3, 3, 3, 4, 5, 3, 0.75),
        (4, 3, 3, 3, 3, 4, 5, 3, 0.72),
        (3, 3, 3, 3, 3, 3, 5, 3, 0.70),
        (3, 3, 2, 3, 3, 3, 4, 4, 0.68),
        (3, 2, 2, 2, 2, 3, 4, 4, 0.65),
    ]
    hook, clarity, novelty, emotion, share, education, safety, edit, confidence = rows[index % len(rows)]
    return ClipScoreSchema(
        hook_strength=hook,
        standalone_clarity=clarity,
        novelty=novelty,
        emotional_intensity=emotion,
        shareability=share,
        educational_value=education,
        brand_safety=safety,
        editing_complexity=edit,
        confidence=confidence,
    )


def make_smoke_engine(local_db: bool) -> tuple[Engine, tempfile.TemporaryDirectory[str] | None, Path]:
    if local_db:
        db_path = BACKEND / "clipops.db"
        return make_engine(f"sqlite:///{db_path.as_posix()}"), None, db_path
    temp_dir = tempfile.TemporaryDirectory(prefix="clipops-smoke-")
    db_path = Path(temp_dir.name) / "clipops-smoke.db"
    return make_engine(f"sqlite:///{db_path.as_posix()}"), temp_dir, db_path


def post_ok(client: TestClient, path: str, payload: dict[str, object]) -> dict[str, object]:
    response = client.post(path, json=payload)
    check(response.status_code < 400, f"{path} failed: {response.status_code} {response.text}")
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ClipOps feature smoke test.")
    parser.add_argument(
        "--local-db",
        action="store_true",
        help="Write demo records to backend/clipops.db so the running UI can load them.",
    )
    args = parser.parse_args()

    engine, temp_dir, db_path = make_smoke_engine(args.local_db)
    app.state.engine = engine
    client: TestClient | None = None

    try:
        Base.metadata.create_all(engine)
        seed(engine)
        client = TestClient(app)
        initial_dashboard = client.get("/dashboard").json()
        initial_queue_status = int(initial_dashboard["queue_status"])

        raw_srt = SRT_FIXTURE.read_text()
        srt = parse_srt(raw_srt)
        check(len(srt.blocks) == 20, "Expected 20 SRT blocks.")
        check(srt.issues == [], f"Expected no SRT issues, got {srt.issues}.")
        pass_line("SRT import", "blocks=20 issues=0")

        source_id = f"source-smoke-{uuid4()}"
        transcript_id = f"transcript-smoke-{uuid4()}"
        validation = post_ok(
            client,
            "/transcripts/validate",
            {
                "transcript_id": transcript_id,
                "source_content_id": source_id,
                "source_title": "Smoke test 2-minute SRT",
                "raw_text": raw_srt,
            },
        )
        check(validation == {"transcript_id": transcript_id, "line_count": 20, "warnings": []}, str(validation))
        pass_line("Transcript validation", "line_count=20 warnings=[]")

        segments_response = client.get(f"/transcripts/{transcript_id}/segments")
        check(segments_response.status_code == 200, segments_response.text)
        segments = segments_response.json()
        ranges = [(segment["start_seconds"], segment["end_seconds"]) for segment in segments]
        check(ranges == [(0, 54), (60, 114)], f"Unexpected segment ranges: {ranges}")
        pass_line("Segmentation", "segments=2 ranges=0-54,60-114")

        workflow = run_workflow(
            engine,
            srt.normalized_text,
            source_content_id=source_id,
            account_profile_id="acct-focus-lab",
        )
        workflow_id = str(workflow["workflow_run_id"])
        check(workflow["status"] == "COMPLETED", f"Workflow failed: {workflow}")
        check(len(workflow["moments"]) == 6, f"Expected 6 moments, got {len(workflow['moments'])}.")

        with Session(engine) as session:
            candidates = session.scalars(
                select(ClipCandidate)
                .where(ClipCandidate.workflow_run_id == workflow_id)
                .order_by(ClipCandidate.start_seconds, ClipCandidate.id)
            ).all()
            check(len(candidates) == 6, f"Expected 6 candidates, got {len(candidates)}.")
            for index, candidate in enumerate(candidates):
                save_score(session, candidate.id, score_input(index))

        with Session(engine) as session:
            asset_count = len(
                session.scalars(
                    select(GeneratedAsset)
                    .join(ClipCandidate, GeneratedAsset.candidate_id == ClipCandidate.id)
                    .where(ClipCandidate.workflow_run_id == workflow_id)
                ).all()
            )
        check(asset_count == 54, f"Expected 54 generated assets, got {asset_count}.")
        pass_line("Workflow", f"status=COMPLETED workflow_run_id={workflow_id} candidates=6 assets=54")

        runs = client.get("/workflow-runs").json()
        run_row = next((run for run in runs if run["workflow_run_id"] == workflow_id), None)
        check(run_row is not None, "Workflow run was not listed.")
        check(len(run_row["model_runs"]) >= 1, "Workflow history did not include model metadata.")
        pass_line("Workflow history", f"run listed model_runs={len(run_row['model_runs'])}")

        candidate_rows = client.get(f"/workflow-runs/{workflow_id}/candidates").json()
        check(len(candidate_rows) == 6, f"Expected 6 candidate rows, got {len(candidate_rows)}.")
        check(candidate_rows[0]["scores"]["overall_score"] >= candidate_rows[-1]["scores"]["overall_score"], "Candidates were not score-ranked.")
        top_candidate_id = candidate_rows[0]["candidate_id"]
        second_candidate_id = candidate_rows[1]["candidate_id"]
        pass_line("Candidate list", f"rows=6 top_score={candidate_rows[0]['scores']['overall_score']}")

        detail = client.get(f"/candidates/{top_candidate_id}").json()
        check(len(detail["assets"]) == 9, f"Expected 9 assets, got {len(detail['assets'])}.")
        asset_id = detail["assets"][0]["id"]
        patched = client.patch(
            f"/candidates/{top_candidate_id}/assets/{asset_id}",
            json={"content": "Edited smoke-test asset."},
        ).json()
        check(patched["content"] == "Edited smoke-test asset.", str(patched))
        pass_line("Candidate detail/assets", "assets=9 patched_asset=ok")

        submitted = post_ok(client, f"/candidates/{top_candidate_id}/review", {"action": "SUBMIT_FOR_REVIEW"})
        check(submitted["status"] == "NEEDS_REVIEW", str(submitted))
        approved = post_ok(client, f"/candidates/{top_candidate_id}/review", {"action": "APPROVE"})
        check(approved["status"] == "APPROVED", str(approved))

        post_ok(client, f"/candidates/{second_candidate_id}/review", {"action": "SUBMIT_FOR_REVIEW"})
        rejected_without_reason = client.post(f"/candidates/{second_candidate_id}/review", json={"action": "REJECT"})
        check(rejected_without_reason.status_code == 422, rejected_without_reason.text)
        rejected = post_ok(
            client,
            f"/candidates/{second_candidate_id}/review",
            {"action": "REJECT", "reason": "Smoke test rejection reason."},
        )
        check(rejected["status"] == "REJECTED", str(rejected))
        pass_line("Review lifecycle", "submit=NEEDS_REVIEW approve=APPROVED reject_requires_reason=true")

        queue = post_ok(
            client,
            f"/candidates/{top_candidate_id}/queue",
            {"scheduled_for": "2026-08-01T09:00:00Z"},
        )
        check(queue["status"] == "QUEUED", str(queue))
        publishing_queue = client.get("/publishing-queue").json()
        check(any(item["queue_item_id"] == queue["queue_item_id"] for item in publishing_queue), str(publishing_queue))
        pass_line("Publishing queue", f"queue_item_id={queue['queue_item_id']} status=QUEUED")

        performance = post_ok(
            client,
            "/performance-records",
            {"queue_item_id": queue["queue_item_id"], "views": 1200, "engagement_rate": 0.12},
        )
        check(performance["simulated"] is True, str(performance))
        pass_line("Performance import", f"performance_record_id={performance['performance_record_id']} simulated=true")

        dashboard = client.get("/dashboard").json()
        check(dashboard["simulated"] is True, str(dashboard))
        check(dashboard["queue_status"] == initial_queue_status + 1, str(dashboard))
        pass_line(
            "Dashboard",
            f"simulated=true queue_status={dashboard['queue_status']} (+1) approval_rate={dashboard['approval_rate']:.3f}",
        )

        experiment = post_ok(
            client,
            "/experiments",
            {
                "id": f"experiment-smoke-{uuid4()}",
                "name": "Smoke hook comparison",
                "hypothesis": "A direct problem hook will outperform a curiosity hook in simulated data.",
                "primary_metric": "engagement_rate",
                "variant_a": "Direct problem hook",
                "variant_b": "Curiosity hook",
                "result_summary": "Direct problem hook led the simulated readout.",
                "winner": "Direct problem hook",
                "confidence_note": "Simulated smoke-test data only; no causal claim.",
            },
        )
        check(experiment["name"] == "Smoke hook comparison", str(experiment))
        pass_line("Experiment", "name=Smoke hook comparison winner=Direct problem hook")

        report = post_ok(client, "/weekly-reports", {})
        check(report["simulated"] is True, str(report))
        check(report["top_clips"], "Expected at least one top clip.")
        check(report["caveats"], "Expected report caveats.")
        pass_line("Weekly report", f"simulated=true top_clips={len(report['top_clips'])} caveats={len(report['caveats'])}")

        print()
        print("Feature smoke test complete.")
        print(f"Database: {db_path}")
        if args.local_db:
            print(f"UI workflow_run_id: {workflow_id}")
            print("Paste that workflow_run_id into the Review queue panel and click Load queue.")
        else:
            print("This was an isolated temp database run. Use --local-db to seed data for the running UI.")
    finally:
        if client is not None:
            client.close()
        app.state.engine = None
        engine.dispose()
        if temp_dir:
            temp_dir.cleanup()


if __name__ == "__main__":
    main()
