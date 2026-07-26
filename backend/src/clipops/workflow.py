from typing import TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from clipops.model_provider import (
    MockModelProvider,
    ModelProvider,
    MomentDraft,
    SegmentInput,
    record_model_run,
)
from clipops.models import Base, WorkflowRun
from clipops.segmentation import Segment, segment_transcript
from clipops.transcript_validation import validate_transcript


class WorkflowState(TypedDict, total=False):
    raw_text: str
    workflow_run_id: str
    segments: list[Segment]
    moments: list[MomentDraft]
    error: str
    status: str


def build_workflow(engine: Engine, provider: ModelProvider):
    def validate(state: WorkflowState) -> WorkflowState:
        result = validate_transcript(state["raw_text"])
        if result.issues:
            return {"error": result.issues[0].message}
        return {}

    def segment(state: WorkflowState) -> WorkflowState:
        if state.get("error"):
            return {}
        return {"segments": segment_transcript(state["raw_text"])}

    def detect(state: WorkflowState) -> WorkflowState:
        if state.get("error"):
            return {}
        moments = provider.detect_moments(
            [SegmentInput(segment.start_seconds, segment.end_seconds, segment.text) for segment in state["segments"]]
        )
        with Session(engine) as session:
            record_model_run(session, state["workflow_run_id"], provider, "moment-detection-v1", "VALID")
        return {"moments": moments}

    def finish(state: WorkflowState) -> WorkflowState:
        status = "FAILED" if state.get("error") else "COMPLETED"
        with Session(engine) as session:
            run = session.get(WorkflowRun, state["workflow_run_id"])
            if run:
                run.status = status
                run.error_message = state.get("error")
                session.commit()
        return {"status": status}

    graph = StateGraph(WorkflowState)
    graph.add_node("validate", validate)
    graph.add_node("segment", segment)
    graph.add_node("detect", detect)
    graph.add_node("finish", finish)
    graph.add_edge(START, "validate")
    graph.add_edge("validate", "segment")
    graph.add_edge("segment", "detect")
    graph.add_edge("detect", "finish")
    graph.add_edge("finish", END)
    return graph.compile()


def run_workflow(engine: Engine, raw_text: str, provider: ModelProvider | None = None) -> WorkflowState:
    Base.metadata.create_all(engine)
    workflow_run_id = str(uuid4())
    with Session(engine) as session:
        session.add(WorkflowRun(id=workflow_run_id, status="RUNNING"))
        session.commit()
    return build_workflow(engine, provider or MockModelProvider()).invoke(
        {"raw_text": raw_text, "workflow_run_id": workflow_run_id}
    )
