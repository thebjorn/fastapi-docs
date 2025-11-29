---
title: Webhooks
order: 2
description: Real-time event notifications
---

# Webhooks

Webhooks allow you to receive real-time notifications when events occur in your account.

## Setting Up Webhooks

Configure your webhook endpoint in the dashboard or via API:

```python
import requests

webhook_config = {
    "url": "https://your-server.com/webhook",
    "events": ["user.created", "order.completed"],
    "secret": "your-webhook-secret"
}

response = requests.post(
    "https://api.example.com/v1/webhooks",
    json=webhook_config,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

## Verifying Webhook Signatures

Always verify the webhook signature to ensure the request is legitimate:

```python
import hmac
import hashlib

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify the webhook signature matches the payload."""
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)
```

!!! danger
    Never skip signature verification in production! This protects against forged webhook requests.

## Event Types

| Event | Description |
|-------|-------------|
| `user.created` | New user registration |
| `user.updated` | User profile changes |
| `order.created` | New order placed |
| `order.completed` | Order fulfilled |
