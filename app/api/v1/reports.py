"""Reporting endpoints for order history and analytics."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db import models
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

@router.get("/orders")
def order_history_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, le=500),
    db: Session = Depends(get_db)
):
    # PERFORMANCE ISSUE: Full table scan — no indexes on status+created_at
    # Uses OFFSET pagination — slow on large datasets
    # TODO: add composite index on (status, created_at DESC)
    # TODO: switch to cursor-based (keyset) pagination
    offset = (page - 1) * page_size
    query = db.query(models.Order)
    if start_date:
        query = query.filter(models.Order.created_at >= start_date)
    if end_date:
        query = query.filter(models.Order.created_at <= end_date)
    if status:
        query = query.filter(models.Order.status == status)
    return query.order_by(models.Order.created_at.desc()).offset(offset).limit(page_size).all()

@router.get("/revenue")
def revenue_report(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    since = datetime.utcnow() - timedelta(days=days)
    result = db.query(
        func.sum(models.Order.total_amount).label("total_revenue"),
        func.count(models.Order.id).label("order_count"),
        func.avg(models.Order.total_amount).label("avg_order_value"),
    ).filter(
        models.Order.status == models.OrderStatus.PAID,
        models.Order.created_at >= since
    ).first()
    return {
        "total_revenue": result.total_revenue or 0,
        "order_count": result.order_count or 0,
        "avg_order_value": result.avg_order_value or 0,
        "period_days": days
    }
