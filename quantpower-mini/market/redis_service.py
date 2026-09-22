import json

import redis
from django.conf import settings


redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


def save_tick(security_id, tick):
    key = f"market:tick:{security_id}"

    redis_client.set(
        key,
        json.dumps(tick),
        ex=60,
    )


def get_tick(security_id):
    key = f"market:tick:{security_id}"

    data = redis_client.get(key)

    if not data:
        return None

    return json.loads(data)


def publish_tick(tick):
    channel = "market:ticks"

    redis_client.publish(
        channel,
        json.dumps(tick),
    )