import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from werkzeug.wrappers import Request, Response
from backend.app import app as flask_app


def handler(request):
    """Vercel handler - wraps Flask app for Vercel serverless"""
    return flask_app(request)


# For local testing with `vercel dev`
app = handler
