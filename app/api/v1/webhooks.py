"""Stripe webhook handler — receives payment lifecycle events."""
from fastapi import APIRouter, Request, HTTPException
from app.core.config import settings
import stripe
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    # TODO: add idempotency check — Stripe delivers events multiple times
    # TODO: process events asynchronously via Celery
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "payment_intent.succeeded":
        logger.info(f"Payment succeeded: {event['data']['object']['id']}")
        # TODO: update order status, trigger fulfillment
    elif event["type"] == "payment_intent.payment_failed":
        logger.warning(f"Payment failed: {event['data']['object']['id']}")
        # TODO: update order status, notify user
    elif event["type"] == "customer.subscription.deleted":
        logger.info(f"Subscription cancelled: {event['data']['object']['id']}")
        # TODO: deactivate subscription features, send retention email
    else:
        logger.debug(f"Unhandled event type: {event['type']}")

    # Must return 200 quickly — Stripe retries on non-200
    return {"status": "received"}
