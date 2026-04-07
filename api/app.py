import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import app as flask_app


# Vercel handler - must be at top level
def handler(request):
    with flask_app.test_client() as client:
        response = client.open(
            path=request.path,
            method=request.method,
            query_string=request.query_string.decode('utf-8'),
            headers=dict(request.headers),
        )
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.data.decode('utf-8')
        }


# Required by Vercel
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
