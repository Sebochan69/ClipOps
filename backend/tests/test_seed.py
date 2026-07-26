from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from clipops.models import AccountProfile, ContentBrief, Transcript
from clipops.seed import seed


def test_seed_is_idempotent() -> None:
    engine = create_engine("sqlite://")
    seed(engine)
    seed(engine)

    with Session(engine) as session:
        accounts = session.scalars(select(AccountProfile)).all()
        assert {account.name for account in accounts} == {"Focus Lab", "Maker Notes", "Systems Minute"}
        assert all("Fictional demo account." == account.details["historical_notes"] for account in accounts)
        assert len(session.scalars(select(ContentBrief)).all()) == 2
        assert len(session.scalars(select(Transcript)).all()) == 1
