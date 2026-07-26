import json
from pathlib import Path

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from clipops.database import make_engine
from clipops.models import AccountProfile, Base, ContentBrief, SourceContent, Transcript
from clipops.schemas import AccountProfileSchema, ContentBriefSchema

DATA_DIR = Path(__file__).resolve().parents[3] / "seed-data"


def seed(engine: Engine, data_dir: Path = DATA_DIR) -> None:
    Base.metadata.create_all(engine)
    accounts = [AccountProfileSchema.model_validate(row) for row in json.loads((data_dir / "accounts.json").read_text())]
    briefs = [ContentBriefSchema.model_validate(row) for row in json.loads((data_dir / "briefs.json").read_text())]
    transcript = (data_dir / "demo-transcript.md").read_text()

    with Session(engine) as session:
        for account in accounts:
            if not session.get(AccountProfile, account.id):
                session.add(AccountProfile(id=account.id, name=account.name, platform=account.platform, details=account.model_dump()))
        for brief in briefs:
            if not session.get(ContentBrief, brief.id):
                session.add(ContentBrief(id=brief.id, name=brief.name, objective=brief.objective, details=brief.model_dump()))
        if not session.get(SourceContent, "source-focus-session"):
            session.add(SourceContent(id="source-focus-session", title="Focus session"))
            session.add(Transcript(id="transcript-focus-session", source_content_id="source-focus-session", raw_text=transcript))
        session.commit()


def main() -> None:
    seed(make_engine())


if __name__ == "__main__":
    main()
