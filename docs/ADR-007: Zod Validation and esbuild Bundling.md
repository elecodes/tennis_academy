# ADR-007: Zod Validation and esbuild Bundling

## Status
Accepted

## Context
The project initially relied on simple `required` HTML attributes and basic server-side validation for form handling. As the complexity of forms grew (e.g., Manage Users, Groups, Enrollments), we needed a more robust, type-safe way to handle client-side validation without introducing a heavy frontend framework like React or Vue. We wanted to keep the "Vanilla JS" philosophy but improve developer experience and data integrity.

## Decision
We decided to integrate **Zod** for schema-based validation. To support TypeScript and Zod in a browser-friendly way within our existing Jinja2 templates, we introduced **esbuild** as a lightweight bundler.

1.  **Zod**: Used for defining schemas that can be reused across different forms.
2.  **esbuild**: Used to bundle the TypeScript validation logic into a single JavaScript file (`frontend/static/js/dist/validations.js`).
3.  **Global Interface**: The validation functions are exposed to the `window` object via `window.Validations`, allowing them to be called directly from script blocks in regular HTML templates.

## Consequences
- **Improved Reliability**: Client-side validation is now schema-driven and more comprehensive (regex, email formats, min/max lengths).
- **Lightweight Build Step**: Developers need to run `npm run build:js` (or `npm run dev` equivalents) when modifying validation schemas.
- **Vanilla JS Compatibility**: We maintain the ability to use simple `<script>` tags in templates while gaining modern validation tools.
- **Dependency Management**: Added `npm` dependencies (`zod`, `esbuild`) to the root of the project.
