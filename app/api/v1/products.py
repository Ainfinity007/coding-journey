"""Product catalog and search endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.db import models
from typing import Optional, List

router = APIRouter()

@router.get("/")
def list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(models.Product).filter(models.Product.is_active == True)
    if category:
        query = query.filter(models.Product.category == category)
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    if in_stock:
        query = query.filter(models.Product.stock > 0)
    # Simple search — no full-text search or Elasticsearch yet
    # TODO: replace with Elasticsearch full-text search
    return query.offset(skip).limit(limit).all()

@router.get("/search")
def search_products(
    q: str = Query(..., min_length=1),
    category: Optional[List[str]] = Query(None),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    min_rating: Optional[float] = None,
    sort: str = "relevance",
    cursor: Optional[str] = None,
    limit: int = Query(default=20, le=50),
    db: Session = Depends(get_db)
):
    # TODO: This is a naive SQL LIKE search — not production-ready
    # Replace entire implementation with Elasticsearch query
    query = db.query(models.Product).filter(
        models.Product.is_active == True,
        or_(
            models.Product.name.ilike(f"%{q}%"),
            models.Product.description.ilike(f"%{q}%")
        )
    )
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    return query.limit(limit).all()

@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
