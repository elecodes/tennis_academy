# ADR-002: Vanilla JS Modal System

## Status
✅ **ACCEPTED**

**Date**: 2026-02-20

## Context
The application initially relied on Bootstrap 5 for modal functionality. However, inconsistencies in the Bootstrap JS integration led to "Add" buttons (users, groups, enrollments) failing to trigger modals reliably across different environments. Additionally, we wanted a more premium, custom look that aligned with the new "SF Tennis" design system.

## Decision
Implement a lightweight, custom **Vanilla JavaScript Modal System** integrated into `base.html`.

### Core Requirements
1. **No Dependencies**: Must work without external JS libraries like Bootstrap or jQuery.
2. **Global Availability**: Any page extending `base.html` can trigger a modal.
3. **Accessibility**: Handle backdrop clicks, escape key, and body scroll locking.
4. **Premium UX**: Smooth transitions, backdrop blurring, and centered positioning.

## Implementation

### Interface
```javascript
// Open a modal
window.openModal('modalId');

// Close a modal
window.closeModal('modalId');
```

### Structure (`base.html`)
```html
<div id="modalId" class="modal-overlay hidden">
    <div class="modal-content">
        <!-- Form Content -->
    </div>
</div>
```

### Styling
- **Backdrop**: `bg-navy/40 backdrop-blur-md`
- **Positioning**: Fixed, centered using Flexbox.
- **Animation**: Subtle scale and opacity transitions.

## Consequences

### Positive
- ✅ **Reliability**: Zero dependency on external JS initialization.
- ✅ **Performance**: Minimal footprint compared to full UI frameworks.
- ✅ **Consistency**: Identical interaction patterns across all admin modules.
- ✅ **Design**: Perfect alignment with the custom premium typography and color palette.

### Negative
- ⚠️ **Manual Setup**: Requires explicit ID management for each modal.
- ⚠️ **No Auto-Init**: Forms must be manually wrapped in the overlay structure.

## Testing Strategy
- **Manual Verification**: Verified opening/closing on Users, Groups, Enrollments, and Timetable pages.
- **Escape Key**: Confirmed modals close on 'Esc' press.
- **Outside Click**: Confirmed modals close when clicking the backdrop.
- **Scroll Lock**: Verified `overflow: hidden` is applied to `body` when modal is active.

## Related Files
- `templates/base.html` - System implementation
- `templates/admin/users.html` - Usage example
- `templates/admin/groups.html` - Usage example
- `templates/admin/enrollments.html` - Usage example
- `templates/timetable.html` - Usage example
