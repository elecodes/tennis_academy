# ADR-022: Mobile UI Refinements and Space Optimization

## Status
Accepted

## Context
The "SF TENNIS KIDS" club application is increasingly accessed via mobile devices. The previous horizontal timetable layout and the Admin Groups Management table were too wide for mobile screens, leading to horizontal scrolling or overlapping text. Specifically, the "Capacity" (student counts/avatars) field was identified as low-priority information for the immediate timetable view, occupying valuable screen real estate.

## Decision
We have implemented several UI refinements focused on mobile-first optimization and reclaiming screen space:

1.  **Hiding Capacity Information**:
    *   **Public/Family Timetable**: The "Cohort Size" (capacity) section in group headers is now conditionally hidden. This removes the student count and individual kid avatars, allowing the Group Name and Coach to be more prominent.
    *   **Admin Groups Management**: The "Capacity" column has been removed from the main table. This reclaimed horizontal space allows the Group Name, Coach, and Schedule fields to fit better without layout breaks.

2.  **Optimizing Schedule/Time Display**:
    *   Session cards now display the full time range (`Start Time - End Time`) on a single line. This improves clarity for families without needing to expand or click for more details.

3.  **Mobile Navigation (Timetable)**:
    *   **Horizontal Day Selector**: Replaced the previous 7x1 grid with a horizontally scrollable tab list for choosing days on mobile.
    *   **Group Accordions**: implemented an accordion-style list for groups within a day, allowing users to focus on one group at a time.

## Consequences
- **Positive**: Significantly improved readability on mobile devices. Reduced visual clutter. Reclaimed space for core "When and Where" details.
- **Negative**: Admin users can no longer see the member count directly in the groups list (they must visit the enrollment page or edit the group if a count is needed).
- **Next Steps**: The "Schedule" text field in the groups table is still considered "messy" and contains redundant info; a future refinement will focus on structuring this data more cleanly or using a more compact badge-based display.

## Date
2026-03-17
