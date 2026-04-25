# ADR-025: PWA Icon Fix for Android Home Screen

## Status
Accepted

## Context
When users added the SF Tennis Kids Club web app to their Android home screen via "Add to Home Screen", the icon displayed as a generic letter "V" (from the app name) instead of the intended tennis ball logo. Investigation revealed three independent root causes:

1. **Corrupt PNG files**: The icon files (`icon-192.png`, `icon-512.png`) in `frontend/static/icons/` were actually JPEG images mislabeled with `.png` extensions. Android's manifest validator strictly checks magic bytes and rejected them as invalid PNGs.

2. **Invalid manifest purpose**: The `manifest.json` declared icon purposes as `"any maskable"` (combined string). This is deprecated and ignored by most modern Android browsers; purposes must be declared as separate icon entries.

3. **Vercel routing conflict**: The `vercel.json` configuration included a `/static/:path*` route that intercepted static file requests and returned 404 errors in production, preventing the browser from fetching icons.

## Decision

### 1. Regenerate Valid PNG Icons
Used Python PIL to properly convert the source images into true PNG format with RGBA transparency support:
```python
from PIL import Image
img = Image.open("source.jpg").convert("RGBA")
img = img.resize((192, 192), Image.LANCZOS)
img.save("icon-192.png", "PNG")
```

### 2. Split Manifest Icon Purposes
Updated `manifest.json` to declare separate icon entries for `"any"` (standard display) and `"maskable"` (adaptive icon with safe zone):
```json
{
  "icons": [
    { "src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable" },
    { "src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
    { "src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

### 3. Simplify Vercel Routing
Removed the erroneous `/static/:path*` rewrite rule from `vercel.json`. All requests now fall through to the Flask backend catch-all route, which correctly serves static files via Flask's built-in static handler.

### 4. Cache Busting
Bumped the version query parameter on manifest, favicon, and apple-touch-icon links in `base.html` from `v3` to `v6` to force Android browsers to bypass cached broken icons.

## Consequences
- **Positive**: Android home screen icons now display the tennis ball logo correctly.
- **Positive**: Static assets are reliably served in production via Flask's static handler.
- **Positive**: Manifest follows current PWA best practices with separated icon purposes.
- **Negative**: Users who previously added the app to their home screen must remove and re-add the shortcut to see the updated icon.
- **Lesson**: Always validate that image files match their declared format (use `file` command or magic byte inspection) before deployment.
