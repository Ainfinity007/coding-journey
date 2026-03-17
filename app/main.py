"""
FastAPI E-Commerce Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import users, orders, products, auth, notifications, reports
from app.core.config import settings
from app.db.session import engine
from app.db import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
