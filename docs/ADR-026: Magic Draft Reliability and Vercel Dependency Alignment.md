# ADR-026: Magic Draft Reliability and Vercel Dependency Alignment

## Status
Accepted

## Context
The Magic Draft feature started failing in Vercel production with `500` responses on `/api/draft-message`. Logs showed `AI draft feature not available - genkit not installed`, which indicated runtime dependency and failure-handling gaps:

1. AI failures were collapsed into generic `500` errors, reducing operator visibility and user guidance.
2. Legacy clients still posted to `/admin/api/draft-message`, while newer clients used `/api/draft-message`.
3. Vercel's Python function needed explicit dependency alignment with the serverless entrypoint to ensure `genkit` plugins are installed.

## Decision
We implemented the following:

1. **Typed AI errors and status mapping**
   - Introduced `AIDraftUnavailableError` (returns `503`) and `AIDraftProviderError` (returns `502`).
   - Kept `500` only for unexpected failures.

2. **Route compatibility**
   - Kept `/api/draft-message` as primary endpoint.
   - Added `/admin/api/draft-message` as a compatibility alias to avoid stale-client breakage during rollout.

3. **Vercel dependency alignment**
   - Added `api/requirements.txt` with runtime dependencies, including:
     - `genkit==0.5.1`
     - `genkit-plugin-google-genai==0.5.1`
   - Updated `vercel.json` install command to install from `api/requirements.txt`.

4. **Frontend fallback messaging**
   - Added explicit user-facing handling for `502` and `503` responses in admin/coach send-message templates.

## Consequences
- **Positive**: Production no longer hides expected AI outages behind generic `500` responses.
- **Positive**: Existing deployed frontend bundles continue working during transition thanks to endpoint aliasing.
- **Positive**: Vercel runtime dependencies are now declared where the serverless function resolves installs.
- **Negative**: Temporary dual-endpoint support must be maintained until old clients are fully invalidated.
- **Operational**: `GEMINI_API_KEY` (or `GOOGLE_GENAI_API_KEY`) remains a required production environment variable.
