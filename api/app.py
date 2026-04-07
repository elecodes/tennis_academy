import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Try using Flask's wsgi_to_asgi or direct handler
from werkzeug.wrappers import Request as WerkzeugRequest

# Import Flask app
from backend.app import app as flask_app


def handler(request):
    """Vercel handler using Flask's test client for simplicity"""
    # Use Flask's test client to handle the request
    with flask_app.test_client() as client:
        # Convert Vercel request to Flask test request
        response = client.open(
            path=request.path,
            method=request.method,
            query_string=request.query_string.decode("utf-8"),
            headers=dict(request.headers),
        )

        return {
            "statusCode": response.status_code,
            "headers": dict(response.headers),
            "body": response.data.decode("utf-8"),
        }


# For local testing
app = handler
