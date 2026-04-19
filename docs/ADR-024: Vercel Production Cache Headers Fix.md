# ADR-024: Vercel Production Cache Headers Fix

## Status
Accepted

## Context
When deploying the application to Vercel production (`VERCEL=1` and `debug=False`), users experienced a `500 Internal Server Error` exclusively on routes protected by the `@cache_response` decorator (such as after a successful login or accessing protected dashboard pages). 

Upon investigation, the root cause was identified in the `cache_response` decorator in `backend/app.py`. The decorator attempted to directly modify the `headers` attribute of the response object returned by the route. However, in production mode, Flask route functions returning string literals (rendered HTML templates) are not automatically converted into full `Response` objects before the decorator executes. Consequently, accessing `.headers` on a Python `str` object raised an `AttributeError`.

This issue did not surface in local development because `app.debug = True` handles the response lifecycle differently, inadvertently masking the error.

## Decision
We updated the `@cache_response` decorator to wrap the route's return value using Flask's `make_response()` function before attempting to modify its headers.

```python
from flask import make_response

def cache_response(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # ...
        # Wrap return value in make_response to guarantee a Response object
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'private, max-age=120'
        return response
    return decorated_function
```

This guarantees that `response` is always a valid Flask `Response` object with a `.headers` dictionary, regardless of the environment (`debug=True` vs `debug=False`).

## Consequences
- **Positive**: The `500 Internal Server Error` in production environments is resolved. Private caching behavior is preserved.
- **Positive**: Best practices are adhered to by standardizing response manipulation in Flask decorators.
- **Negative**: Negligible overhead by explicitly calling `make_response()`, which Flask would ultimately do anyway internally.
