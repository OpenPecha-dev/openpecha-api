from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings, get_settings

settings = get_settings()
