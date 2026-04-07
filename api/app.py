import sys
import os

# Fix path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Try to import, capture any errors
try:
    from app import app as flask_app
except Exception as e:
    print(f"Import error: {e}", file=sys.stderr)

    # Return error as response
    def handler(request):
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "text/plain"},
            "body": f"Import error: {str(e)}",
        }

    app = handler
else:
    # If import successful, use test client
    def handler(request):
        with flask_app.test_client() as client:
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

    app = handler
