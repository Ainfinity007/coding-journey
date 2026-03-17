"""
OrderService — monolithic service handling all order-related business logic.
This class has grown too large and handles too many concerns.
TODO: Refactor into separate services (PricingService, InventoryService, FulfillmentService)
"""
from sqlalchemy.orm import Session
from app.db import models
from app.core.config import settings
import stripe
import logging

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, user_id: int, items: list, shipping_address: dict):
        """Create order, reserve inventory, calculate pricing."""
        total = self._calculate_total(items)
        discounted = self._apply_discounts(user_id, total)
        tax = self._calculate_tax(discounted, shipping_address)
        grand_total = discounted + tax
        for item in items:
            self._reserve_inventory(item["product_id"], item["quantity"])
        order = models.Order(
            user_id=user_id,
            total_amount=grand_total,
            shipping_address=shipping_address,
            status=models.OrderStatus.PENDING
        )
        self.db.add(order)
        self.db.flush()
        for item in items:
            product = self.db.query(models.Product).get(item["product_id"])
            order_item = models.OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=product.price
            )
            self.db.add(order_item)
        self.db.commit()
        self._send_order_confirmation_email(user_id, order.id, grand_total)
        logger.info(f"Order {order.id} created for user {user_id}")
        return order

    def _calculate_total(self, items: list) -> float:
        total = 0.0
        for item in items:
            product = self.db.query(models.Product).get(item["product_id"])
            if not product:
                raise ValueError(f"Product {item['product_id']} not found")
            total += product.price * item["quantity"]
        return total

    def _apply_discounts(self, user_id: int, total: float) -> float:
        # TODO: implement discount code system
        # Hardcoded 10% discount for all orders for now
        return total * 0.9

    def _calculate_tax(self, amount: float, shipping_address: dict) -> float:
        # Simplified flat tax rate — should use TaxJar API
        state = shipping_address.get("state", "")
        tax_rates = {"CA": 0.0875, "NY": 0.08, "TX": 0.0625}
        rate = tax_rates.get(state, 0.07)
        return amount * rate

    def _reserve_inventory(self, product_id: int, quantity: int):
        product = self.db.query(models.Product).get(product_id)
        if product.stock < quantity:
            raise ValueError(f"Insufficient stock for product {product_id}")
        product.stock -= quantity

    def process_payment(self, order_id: int, payment_method_id: str):
        order = self.db.query(models.Order).get(order_id)
        # No idempotency key check — race condition possible
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),
            currency="usd",
            payment_method=payment_method_id,
            confirm=True,
        )
        order.stripe_payment_intent_id = intent.id
        order.status = models.OrderStatus.PROCESSING
        self.db.commit()
        return intent

    def _send_order_confirmation_email(self, user_id: int, order_id: int, total: float):
        # TODO: implement via SendGrid
        # Placeholder — emails not actually sent
        logger.info(f"[STUB] Would send order confirmation email for order {order_id}")

    def calculate_shipping(self, order_id: int, shipping_method: str) -> float:
        rates = {"standard": 5.99, "express": 14.99, "overnight": 29.99}
        return rates.get(shipping_method, 5.99)

    def cancel_order(self, order_id: int):
        order = self.db.query(models.Order).get(order_id)
        if order.status not in [models.OrderStatus.PENDING, models.OrderStatus.PROCESSING]:
            raise ValueError("Cannot cancel order in current status")
        order.status = models.OrderStatus.CANCELLED
        for item in order.items:
            product = self.db.query(models.Product).get(item.product_id)
            product.stock += item.quantity
        self.db.commit()

    def refund_order(self, order_id: int):
        order = self.db.query(models.Order).get(order_id)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        refund = stripe.Refund.create(payment_intent=order.stripe_payment_intent_id)
        order.status = models.OrderStatus.REFUNDED
        self.db.commit()
        return refund
