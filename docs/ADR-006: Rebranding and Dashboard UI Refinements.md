# ADR-006: Rebranding and Dashboard UI Refinements

## Status
Accepted

## Context
The "SF TENNIS KIDS CLUB" (formerly referred to as an academy) required a more consistent and professional brand identity across all digital platforms. Additionally, user feedback indicated that the coach dashboard terminology was confusing and the dashboard header had persistence issues.

## Decision
1. **Full Rebranding**: Unified all internal and external references to "**SF TENNIS KIDS CLUB**". 
   - Updated logos, headers, and navigation bars.
   - Clarified "Located at SFSU" to distinguish location from university affiliation.
2. **Coach Dashboard Terminology**:
   - Renamed "Cohorts" to "**My Groups**" to align with common tennis industry language.
   - Renamed "Instructional Command" to "**Send Message**" for clarity and better UX.
3. **Header Persistence**:
   - Isolated the global auto-removal script in `base.html` to target only flash messages (using a specific `.flash-message` class).
   - This prevents the "premium" dashboard header from being inadvertently removed after a few seconds.
4. **Visual Accessibility**:
   - Improved contrast in the main header by explicitly setting the brand title to white against the navy background.

## Consequences
- Improved brand consistency and professional appearance.
- Reduced cognitive load for coaches using the platform.
- More stable and reliable UI experience as the branding header is now persistent.
- clearer communication regarding university association.
