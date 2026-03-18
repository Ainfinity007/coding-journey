# Coding Journey - Platform Backend

A production-ready Python backend platform with authentication, rate limiting,
real-time WebSocket features, and analytics.

## Modules

### Authentication (`auth/`)
- `jwt_handler.py` - JWT token generation and validation (RS256)
- Token pair management (access + refresh tokens)
- FastAPI dependency injection for route protection

### Middleware (`middleware/`)
- `rate_limiter.py` - Redis sliding window rate limiting
- Per-IP and per-user rate limiting
- Configurable via `RATE_LIMIT_RPM` environment variable
- HTTP 429 responses with `Retry-After` headers

### Real-Time (`realtime/`)
- `websocket_manager.py` - WebSocket connection manager
- Redis Pub/Sub for horizontal scaling across instances
- Heartbeat support and automatic dead connection cleanup

### Analytics (`analytics/`)
- `pipeline.py` - Buffered analytics event pipeline
- Batch writes to PostgreSQL for efficiency
- Real-time event streaming via Redis for live dashboards

## Environment Variables

```env
RATE_LIMIT_RPM=100          # Requests per minute per IP
REDIS_HOST=localhost         # Redis host
REDIS_PORT=6379             # Redis port
```

## Setup

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Architecture

See Confluence documentation:
- System Architecture Overview
- API Design Standards
- Security and Authentication Guidelines
- Real-Time Features and WebSocket Scaling
