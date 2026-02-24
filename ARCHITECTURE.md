# System Architecture: SF TENNIS KIDS Club

This document outlines the architectural design, technology stack, and core components of the SF TENNIS KIDS Club communication system.

## 1. High-Level Overview
The SF TENNIS KIDS Club platform is a web-based communication system designed to streamline interactions between administrators, coaches, and families. It facilitates group management, enrollment tracking, and automated notifications (e.g., rain cancellations, schedule changes).

## 2. Technology Stack
- **Framework**: [Flask](https://flask.palletsprojects.com/) (Python-based micro-framework).
- **Database**: [SQLite](https://www.sqlite.org/index.html) for data persistence.
- **Templating**: [Jinja2](https://jinja.palletsprojects.com/) for server-side HTML rendering.
- **Authentication**: Session-based with `werkzeug.security` for password hashing.
- **Email/Notifications**: SMTP-based mailing (Gmail integration).
- **Design/Theming**: [DESIGN.md](file:///Users/elena/Developer/tennis_academy/DESIGN.md) defines the "SF TENNIS KIDS" design system (Premium, Academic).

## 3. Architectural Patterns
The project is currently transitioning from a monolithic structure to a more modular architecture:

- **Monolith (Legacy)**: [backend/app.py](file:///Users/elena/Developer/tennis_academy/backend/app.py) contains the core logic, database initialization, and many route handlers.
- **Blueprints**: New features are implemented using Flask Blueprints (e.g., [routes/timetables.py](file:///Users/elena/Developer/tennis_academy/routes/timetables.py)).
- **Repository Pattern**: Data access logic is being abstracted into repositories (e.g., [repositories/timetable_repository.py](file:///Users/elena/Developer/tennis_academy/repositories/timetable_repository.py)) to separate business logic from SQL queries.
- **RBAC (Role-Based Access Control)**: Custom decorators (`@admin_required`, `@coach_required`, `@login_required`) enforce access levels across the system.

## 4. System Components

### 4.1. Core Modules
- **Authentication**: Handles user registration, login, and session management.
- **Group Management**: CRUD operations for tennis groups, including schedules and coach assignments.
- **Enrollment System**: Tracks which families and kids are enrolled in which groups.
- **Messaging Engine**: Sends multi-channel notifications (Internal message board + Email) with receipt tracking.

### 4.2. Recent Features
- **Weekly Timetable**: A structured representation of the club's schedule, filtered by user role.
- **Refined UI**: A premium, mobile-responsive interface across all dashboards.

## 5. Data Model
Key tables in the [academy.db](file:///Users/elena/Developer/tennis_academy/academy.db) database:

- **`users`**: Stores user profiles and roles (`admin`, `coach`, `family`).
- **`groups`**: Definitions of tennis classes.
- **`group_members`**: Junction table for enrollments, linking groups to families and specific kids.
- **`group_schedules`**: Structured weekly slots (Day, Start/End Time, Court).
- **`messages`**: Records sent communications.
- **`message_recipients`**: Tracks delivery status for individual users.

## 6. Request/Response Lifecycle
1. **Request**: Browser hits a route (e.g., `/dashboard`).
2. **Middleware**: Auth decorators verify sessions and roles.
3. **Controller**: The route handler (in `app.py` or a Blueprint) gathers data.
4. **Data Access**: Controllers use Repositories or direct SQL calls to fetch data.
5. **Rendering**: The controller passes data to a Jinja2 template.
6. **Response**: The server returns rendered HTML to the client.

## 7. Deployment & Environment
- **Local Development**: Runs via `python3 backend/app.py` (Port 5001).
- **Environment Variables**: Managed via `.env` files (SMTP credentials, Secret Keys).
- **Production**: Optimized for platforms like Render, using a standard WSGI server.
