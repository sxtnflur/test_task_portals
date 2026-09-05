from config.settings import settings
from infra.db import create_session_factory, create_engine

engine = create_engine(settings.database_url)
session_factory = create_session_factory(engine)
