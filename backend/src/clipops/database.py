from sqlalchemy import Engine, create_engine


def make_engine(url: str = "sqlite:///clipops.db") -> Engine:
    return create_engine(url)
