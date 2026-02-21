
### `skills/high_standards/UX_MICROCOPY.md`
```md
# 🎨 UXMicrocopy

**Source:** UX_AND_MICROCOPY_STANDARDS.md

## tennis_academy Flash Messages

**Nielsen Heuristics:**

**Bootstrap Modals:**
```html
<!-- Loading state -->
<div class="spinner-border" role="status">
  <span class="visually-hidden">Sending notifications...</span>
</div>

<!-- Success -->
<div class="alert alert-success">
  Message sent to 8 families
</div>
Active Voice:

✅ "Enroll Family" 
❌ "Enrollment Processing"
Accessibility:

All modals: role="dialog" aria-labelledby

Flash messages: role="alert"