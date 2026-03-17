"""Order management and payment endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from pydantic import BaseModel
from typing import List, Optional
import stripe
from app.core.config import settings

router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: dict

@router.post("/")
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    # TODO: get user from auth token instead of hardcoding
    total = 0.0
    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
        total += product.price * item.quantity
    order = models.Order(user_id=1, total_amount=total, shipping_address=order_data.shipping_address)
    db.add(order)
    db.flush()
    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        db_item = models.OrderItem(order_id=order.id, product_id=item.product_id,
                                    quantity=item.quantity, unit_price=product.price)
        db.add(db_item)
    db.commit()
    return {"order_id": order.id, "total": total}

@router.post("/{order_id}/pay")
def pay_order(
    order_id: int,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: Session = Depends(get_db)
):
    # BUG: No SELECT FOR UPDATE locking — race condition allows double-charge
    # Two concurrent requests both see status=pending and both proceed
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != models.OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Order is already {order.status}")
    # TODO: check idempotency_key against Redis cache before proceeding
    # TODO: use db.query(models.Order).filter(...).with_for_update().first()
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),
            currency="usd",
            metadata={"order_id": order_id}
        )
        order.status = models.OrderStatus.PROCESSING
        order.stripe_payment_intent_id = intent.id
        db.commit()
        return {"client_secret": intent.client_secret}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
