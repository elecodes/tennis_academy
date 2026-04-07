import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app import app as flask_app


def handler(request):
    """Vercel handler - wraps Flask app for Vercel serverless"""
    # Create WSGI environment from Vercel request
    environ = {
        "REQUEST_METHOD": request.method,
        "SCRIPT_NAME": "",
        "PATH_INFO": request.path or "/",
        "QUERY_STRING": request.query_string.decode("utf-8"),
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "443",
        "HTTP_HOST": request.headers.get("host", "localhost"),
        "wsgi.url_scheme": "https",
        "wsgi.input": None,
        "wsgi.errors": sys.stderr,
    }

    # Add headers
    for key, value in request.headers.items():
        key = key.upper().replace("-", "_")
        if key not in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            key = f"HTTP_{key}"
        environ[key] = value

    # Create start_response callable
    response_body = []

    def start_response(status, headers):
        response_body.append((status, list(headers)))

    # Get response
    response = flask_app(environ, start_response)

    # Get status and body
    status_line, headers = response_body[0]
    status = int(status_line.split()[0])
    body = b"".join(response)

    # Return Vercel response
    return {
        "statusCode": status,
        "headers": dict(headers),
        "body": body.decode("utf-8"),
    }


# For local testing with `vercel dev`
app = handler
