import pytest
from backend.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_security_headers_present(client):
    """Verify that essential security headers are present in the response."""
    response = client.get("/")

    # Check for basic security headers provided by Talisman
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"

    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"

    # Check for Content-Security-Policy
    assert "Content-Security-Policy" in response.headers
    csp = response.headers["Content-Security-Policy"]

    # Verify our custom CSP rules
    assert "default-src 'self'" in csp
    assert (
        "script-src 'self' 'unsafe-inline' cdn.tailwindcss.com browser.sentry-cdn.com"
        in csp
    )
    assert "style-src 'self' 'unsafe-inline' fonts.googleapis.com" in csp
    assert "font-src 'self' fonts.gstatic.com" in csp
    assert "connect-src 'self' *.ingest.sentry.io" in csp
