import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.state.state_builder as state_builder
import app.tracker.progress_tracker as progress_tracker
import app.plan.plan_store as plan_store
import app.tracker.reward_log as reward_log
from app.main import app

# The real files the running app uses. Tests must never change them.
REAL_FILES = [
    Path(state_builder.MOCK_STATE_PATH),
    Path(plan_store.PLAN_PATH),
    Path(reward_log.LOG_PATH),
]
BASELINE = Path(state_builder.BASELINE_STATE_PATH)


def _read(path):
    return path.read_bytes() if path.exists() else None


@pytest.fixture(scope="session", autouse=True)
def real_files_untouched():
    """Fails the test run if any test modified the real state, plan or reward files."""
    before = [_read(p) for p in REAL_FILES]
    yield
    after = [_read(p) for p in REAL_FILES]
    assert before == after, "A test modified the real state, plan or reward files"


@pytest.fixture
def client(tmp_path, monkeypatch):
    """An API client whose state, plan and reward files live in a temp folder,
    starting from baseline_state.json."""
    state_file = tmp_path / "mock_state.json"
    shutil.copyfile(BASELINE, state_file)
    monkeypatch.setattr(state_builder, "MOCK_STATE_PATH", str(state_file))
    monkeypatch.setattr(progress_tracker, "MOCK_STATE_PATH", str(state_file))
    monkeypatch.setattr(plan_store, "PLAN_PATH", str(tmp_path / "weekly_plan.json"))
    monkeypatch.setattr(reward_log, "LOG_PATH", str(tmp_path / "reward_log.json"))
    return TestClient(app)