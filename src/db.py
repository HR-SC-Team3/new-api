from sqlalchemy.orm import sessionmaker

from models import get_engine

_session_factory: sessionmaker | None = None


def get_session_factory() -> sessionmaker:
    """Create the session factory on first use, so importing this module needs no DB."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(get_engine())
    return _session_factory
