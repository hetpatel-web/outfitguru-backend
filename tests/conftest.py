import os
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
  sys.path.insert(0, str(ROOT_DIR))

from app.db.base import Base
from app.utils.deps import get_db
from app.main import app


@pytest.fixture(scope="function")
def temp_db() -> Generator[str, None, None]:
  fd, path = tempfile.mkstemp(suffix=".db")
  os.close(fd)
  try:
    yield f"sqlite:///{path}"
  finally:
    if os.path.exists(path):
      os.remove(path)


@pytest.fixture(scope="function")
def client(temp_db: str) -> Generator[TestClient, None, None]:
  engine = create_engine(temp_db, connect_args={"check_same_thread": False})
  TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  Base.metadata.create_all(bind=engine)

  def override_get_db():
    db = TestingSessionLocal()
    try:
      yield db
    finally:
      db.close()

  app.dependency_overrides[get_db] = override_get_db

  with TestClient(app) as test_client:
    yield test_client

  app.dependency_overrides.clear()
