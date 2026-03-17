# E-Commerce Backend API

A FastAPI-based e-commerce backend with user management, product catalog, order processing, payment integration, and real-time notifications.

## Architecture

```
app/
  api/v1/          # Route handlers
    auth.py        # Login, logout, token refresh
    users.py       # User profile management
    products.py    # Product catalog and search
    orders.py      # Order creation and payment
    notifications.py  # WebSocket + polling notifications
    reports.py     # Analytics and reporting
    webhooks.py    # Stripe webhook handler
  core/
    config.py      # Environment-based configuration
    security.py    # JWT token utilities, password hashing
  db/
    models.py      # SQLAlchemy ORM models
    session.py     # Database connection management
  services/
    order_service.py  # Monolithic order business logic (pending refactor)
tests/             # Pytest test suite
```

## Key Technologies
- **FastAPI** — async Python web framework
- **PostgreSQL** — primary database via SQLAlchemy ORM
- **Redis** — caching, rate limiting, session storage
- **Stripe** — payment processing and webhooks
- **Elasticsearch** — full-text product search (partially implemented)
- **Celery** — async task queue for webhooks and reports
- **WebSocket** — real-time notification delivery (partially implemented)

## Known TODOs
- Avatar upload to S3 not implemented (`users.py`)
- Refresh token rotation incomplete (`auth.py`)
- Product search uses SQL LIKE instead of Elasticsearch (`products.py`)
- Payment endpoint has race condition — no SELECT FOR UPDATE (`orders.py`)
- No rate limiting on any endpoint
- WebSocket authentication not implemented (`notifications.py`)
- Order reports use OFFSET pagination (slow on large datasets)
- OrderService needs to be split into domain services

## Setup
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
