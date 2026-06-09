import os
import time
import pytest
from backend.app import app
from backend.database import get_config


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestWebhookAuth:
    def test_missing_sync_key_config(self, client):
        """500 if SYNC_API_KEY not configured on server."""
        os.environ.pop("SYNC_API_KEY", None)
        resp = client.post(
            "/api/webhook/sheets-sync",
            json={"action": "sync_all"},
            headers={"X-Sync-Key": "anything"},
        )
        assert resp.status_code == 500
        assert resp.get_json()["status"] == "error"

    def test_missing_header(self, client):
        """401 if X-Sync-Key header is missing."""
        os.environ["SYNC_API_KEY"] = "test-key-123"
        resp = client.post(
            "/api/webhook/sheets-sync",
            json={"action": "sync_all"},
        )
        assert resp.status_code == 401
        assert resp.get_json()["status"] == "error"

    def test_invalid_key(self, client):
        """401 if X-Sync-Key does not match."""
        os.environ["SYNC_API_KEY"] = "test-key-123"
        resp = client.post(
            "/api/webhook/sheets-sync",
            json={"action": "sync_all"},
            headers={"X-Sync-Key": "wrong-key"},
        )
        assert resp.status_code == 401


class TestWebhookActions:
    def test_sync_all_updates_last_sync_at(self, client):
        """sync_all records current timestamp."""
        os.environ["SYNC_API_KEY"] = "test-key-123"
        before = int(time.time())

        resp = client.post(
            "/api/webhook/sheets-sync",
            json={"action": "sync_all", "rows_processed": 42},
            headers={"X-Sync-Key": "test-key-123"},
        )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["rows_processed"] == 42

        last_sync = int(get_config("last_sync_at") or "0")
        assert last_sync >= before

    def test_sync_row_updates_last_sync_at(self, client):
        """sync_row records current timestamp."""
        os.environ["SYNC_API_KEY"] = "test-key-123"
        before = int(time.time())

        resp = client.post(
            "/api/webhook/sheets-sync",
            json={
                "action": "sync_row",
                "sheet": "MONDAY",
                "row": 5,
                "data": ["10am", "Coach A", "Group 1", "Kid Name"],
            },
            headers={"X-Sync-Key": "test-key-123"},
        )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["rows_processed"] == 0

        last_sync = int(get_config("last_sync_at") or "0")
        assert last_sync >= before

    def test_unknown_action(self, client):
        """400 for unknown action."""
        os.environ["SYNC_API_KEY"] = "test-key-123"

        resp = client.post(
            "/api/webhook/sheets-sync",
            json={"action": "nonsense"},
            headers={"X-Sync-Key": "test-key-123"},
        )

        assert resp.status_code == 400
