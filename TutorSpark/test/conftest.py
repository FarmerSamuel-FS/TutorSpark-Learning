import pathlib
import sys

import pytest

# Ensure the project root (where db.py lives) is on sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import db  # now this should work


@pytest.fixture
def temp_db_path(tmp_path, monkeypatch):
    """
    Temporary DB path fixture shared by all tests.

    - Points db.DB_PATH at a temp file
    - Calls db.init_db() so schema exists
    - Returns the temp path in case a test needs it
    """
    test_db = tmp_path / "test_tutorspark.db"
    monkeypatch.setattr(db, "DB_PATH", test_db)
    db.init_db()
    return test_db
