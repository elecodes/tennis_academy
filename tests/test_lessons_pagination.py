import pytest
from unittest.mock import patch
from backend.app import app

@patch("academy_db.fetch_coaches")
@patch("academy_db.fetch_lessons")
def test_neon_lessons_pagination(mock_fetch_lessons, mock_fetch_coaches):
    mock_fetch_lessons.return_value = [
        {"id": i, "title": f"Lesson {i}", "coach_id": 1, "time": "16:00:00"}
        for i in range(1, 25)
    ]
    mock_fetch_coaches.return_value = [{"id": 1, "name": "Coach John"}]

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["role"] = "admin"
            sess["email"] = "admin@tennis.com"
            sess["full_name"] = "Admin User"

        response = client.get("/neon/lessons?page=1&limit=5")
        assert response.status_code == 200
        data = response.get_json()

        assert data["page"] == 1
        assert data["limit"] == 5
        assert data["total"] == 24
        assert data["has_more"] is True
        assert data["remaining"] == 19
        assert len(data["lessons"]) == 5
        assert data["lessons"][0]["coach_name"] == "Coach John"

        # Test page 5 (last page)
        response_p5 = client.get("/neon/lessons?page=5&limit=5")
        assert response_p5.status_code == 200
        data_p5 = response_p5.get_json()
        assert len(data_p5["lessons"]) == 4
        assert data_p5["has_more"] is False
        assert data_p5["remaining"] == 0
