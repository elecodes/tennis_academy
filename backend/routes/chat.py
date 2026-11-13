"""Public, information-only chat assistant (page + JSON endpoint)."""

import os
import threading
import time
from collections import defaultdict, deque

from flask import Blueprint, current_app, jsonify, render_template, request

from services.chat.chat_service import (
    ChatProviderError,
    ChatUnavailableError,
    ChatValidationError,
    MAX_MESSAGE_CHARS,
    answer_question,
)

chat_bp = Blueprint("chat", __name__)

RATE_LIMIT = int(os.environ.get("CHAT_RATE_LIMIT", "12"))  # questions per window per IP
RATE_WINDOW_SECONDS = 60

# Best effort: on serverless hosting each instance keeps its own counters.
_hits = defaultdict(deque)
_hits_lock = threading.Lock()


def _client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _is_rate_limited(ip):
    now = time.monotonic()
    with _hits_lock:
        window = _hits[ip]
        while window and now - window[0] > RATE_WINDOW_SECONDS:
            window.popleft()
        if len(window) >= RATE_LIMIT:
            return True
        window.append(now)

        if len(_hits) > 5000:  # keep memory bounded
            stale = [
                k
                for k, v in _hits.items()
                if not v or now - v[-1] > RATE_WINDOW_SECONDS
            ]
            for key in stale:
                del _hits[key]
        return False


@chat_bp.route("/chat")
def chat_page():
    """Standalone chat page. Embedded as an iframe in the Wix site and the app."""
    return render_template("chat.html", max_chars=MAX_MESSAGE_CHARS)


@chat_bp.route("/api/chat", methods=["POST"])
def api_chat():
    if _is_rate_limited(_client_ip()):
        return (
            jsonify(error="You're asking quickly! Please wait a minute and try again."),
            429,
        )

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Invalid request."), 400

    try:
        reply = answer_question(data.get("messages"))
    except ChatValidationError:
        return jsonify(error="Please type a question first."), 400
    except ChatUnavailableError as e:
        current_app.logger.warning(f"Chat unavailable: {e}")
        return jsonify(error="The assistant is not available right now."), 503
    except ChatProviderError as e:
        current_app.logger.error(f"Chat provider error: {e}")
        return (
            jsonify(error="The assistant is busy. Please try again in a moment."),
            502,
        )
    except Exception as e:
        current_app.logger.error(f"Chat error: {e}")
        return jsonify(error="Something went wrong. Please try again."), 500

    response = jsonify(reply=reply)
    response.headers["Cache-Control"] = "no-store"
    return response
