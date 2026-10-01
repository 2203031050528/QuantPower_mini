# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

QuantPower Mini is a learning-focused Django monolith that clones a retail algo-trading platform: DRF + SimpleJWT, Django Channels on Daphne, MySQL, Redis (cache, pub/sub, Channels layer, Celery broker), and Celery. Brokers are Dhan and (in progress, uncommitted) Fyers. `README (1).md` is the long-form design doc (AWS/VPC/HAProxy/Nginx/systemd details live there).

Live trading is gated by `LIVE_TRADING_ENABLED` (env, default False). Keep it off; never place real orders while developing.

## Commands

```bash
source venv/bin/activate
pip install -r requirements.txt
python manage.py check
python manage.py makemigrations && python manage.py migrate
python manage.py runserver              # dev HTTP (ASGI app in config/asgi.py for WebSockets)
python manage.py mock_market            # fake ticks -> Redis/Channels, no broker needed
python manage.py dhan_market            # real Dhan WebSocket feed
celery -A config worker -l info
python manage.py test                   # all tests
python manage.py test orders.tests.SomeTestCase.test_method   # single test
```

Config comes from `.env` (loaded in `config/settings.py`): `DB_*` (MySQL), `REDIS_URL`, `DEBUG`, `ALLOWED_HOSTS`, `LIVE_TRADING_ENABLED`, `DHAN_CLIENT_ID`, `DHAN_ACCESS_TOKEN`. Tests need MySQL and Redis reachable.

Production runs via `quantpower-daphne.service` and `quantpower-celery.service` (systemd), behind Nginx.

## Architecture

**Market data path** (`market/`): `dhan_feed.py` (Dhan WS client) → `dhan_parser.py` (binary packet parser) → `feed_manager.MarketFeedManager.process_tick`, which does three things per tick: `redis_service.save_tick` (latest tick in Redis, served by the REST market API), `redis_service.publish_tick` (Redis pub/sub), and `router.MarketRouter.route` (fan-out to Channels groups). `consumers.MarketConsumer` serves `ws/market/` (`market/routing.py`). The management commands `dhan_market` / `mock_market` are the long-running feed processes — the feed does not run inside Django/Daphne.

**Trading path** (`orders/`): views call `oms.OrderManagementSystem`. `create_order` validates side/mode (`VIRTUAL`/`LIVE`)/broker and creates a `PENDING` `Order`. `VIRTUAL` orders go through `execute_virtual_order`, which updates `Position` (weighted average price on BUY; SELL fails if exceeding held qty). `LIVE` orders go through a broker adapter chosen from `BROKER_ADAPTERS` (`orders/adapters/dhan.py`, `orders/adapters/fyers.py`). Adding a broker = new adapter with the same shape (`__init__(user)`, `headers`, `get_proxy`, `build_order_payload`, ...) + registry entry.

**Per-user egress** (`proxy/`): each user is allocated an Elastic IP/proxy (`EIPPool`, `ProxyAllocation` models; `allocator.ProxyAllocator`, `services.ProxyService`). Adapters send broker requests via `get_proxy()` so each user's orders leave from their own IP through HAProxy on a proxy EC2; `generate_haproxy.py` renders that config.

**Other apps**: `dhan/` and `fyers/` hold per-user broker account credentials and broker API service wrappers; `strategies/` (strategy models, signals, Celery-executed runner); `backtest/`; `users/`. Celery app is `config/celery.py`, tasks auto-discovered per app.
