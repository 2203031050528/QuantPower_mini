# QuantPower Mini

A learning-focused mini clone of the QuantPower-style retail algorithmic trading platform.

This project intentionally implements a **smaller feature set** and supports **one broker only: Dhan**, while preserving the important architectural ideas of the larger QuantPower system:

- Django monolith
- Django REST Framework
- Django Channels + Daphne
- MySQL
- Redis
- Celery
- Dhan broker integration
- Market-data pipeline
- WebSocket live market updates
- Order Management System (OMS)
- Virtual trading
- Strategy engine
- Backtesting
- Per-user proxy allocation
- HAProxy
- AWS Elastic IP based broker egress
- Nginx
- systemd
- AWS EC2 + RDS + Redis architecture

> **Important:** This project is primarily a learning/practice implementation. Live trading is disabled by default. Never enable live trading without separately validating broker permissions, order behavior, risk controls, credentials, networking, and regulatory requirements.

---

## 1. Project Goal

The goal is to understand how a small production-style trading platform can be designed and deployed.

The project has two major runtime paths:

### Market Data Path

```text
Dhan Market Feed
       |
       v
Dhan Market Feed Client
       |
       v
Binary Packet Parser
       |
       v
Market Feed Manager
       |
       +----------------+
       |                |
       v                v
     Redis          Channels
       |                |
       |                v
       |           WebSocket
       |                |
       v                v
   REST API          Browser
```

### Trading Path

```text
Browser / Strategy
       |
       v
Django REST API
       |
       v
Order Management System
       |
       +--------------------+
       |                    |
       v                    v
Dhan Adapter          Proxy Allocation
                            |
                            v
                       Proxy EC2
                            |
                            v
                         HAProxy
                            |
                            v
                       User Egress EIP
                            |
                            v
                           Dhan
```

---

# 2. What We Built

The project was built incrementally.

## Phase 1 — Project Foundation

Created a Django-based monolithic backend with separate Django applications:

```text
quantpower-mini/
├── config/
├── users/
├── dhan/
├── market/
├── orders/
├── strategies/
├── backtest/
├── proxy/
├── templates/
├── static/
├── manage.py
├── requirements.txt
└── .env
```

Core stack:

- Python
- Django 5
- Django REST Framework
- Django Channels
- Daphne
- Redis
- Celery
- MySQL
- Requests
- PyJWT / Simple JWT
- WebSocket client for Dhan feed
- HAProxy
- Nginx
- AWS

---

# 3. Main Features

## Authentication

Implemented:

- Django users
- JWT authentication
- Login
- JWT refresh
- Authenticated API access

Main API concepts:

```text
/api/auth/login/
/api/auth/refresh/
```

The project uses:

```python
rest_framework_simplejwt.authentication.JWTAuthentication
```

---

# 4. Dhan Account Management

Users can connect a Dhan account to their platform account.

Model:

```text
DhanAccount
```

Important fields:

```text
user
client_id
access_token
is_active
created_at
updated_at
```

The access token is stored against the user's Dhan account.

### Security

Credentials should never be committed to Git.

Environment variables are used for application-level Dhan credentials:

```env
DHAN_CLIENT_ID=
DHAN_ACCESS_TOKEN=
```

For production, secrets should preferably be moved to a proper secrets-management solution.

---

# 5. Dhan Integration

The project isolates Dhan-specific functionality into adapter/client layers.

Example conceptual structure:

```text
dhan/
├── models.py
├── serializers.py
├── views.py
└── services.py

orders/adapters/
└── dhan.py
```

The Dhan adapter is responsible for:

- Access-token handling
- Dhan account lookup
- Order payload generation
- Broker-specific request handling
- Proxy information retrieval

The rest of the application should not need to understand Dhan-specific request formats.

---

# 6. Market / Instrument Management

The project contains an `Instrument` model.

Important fields:

```text
exchange
segment
security_id
symbol
instrument_type
expiry
strike_price
option_type
is_active
created_at
updated_at
```

This allows the application to maintain a normalized instrument representation.

Example:

```text
NIFTY
NSE_FNO
security_id = 12345
```

The security ID is broker/instrument specific and should not be blindly hard-coded for production.

---

# 7. Redis Market Data

Redis is used for fast market-data storage.

The application stores the latest tick using keys such as:

```text
market:tick:<security_id>
```

Example:

```text
market:tick:12345
```

A stored tick follows an internal format similar to:

```json
{
  "symbol": "NIFTY",
  "security_id": "12345",
  "ltp": 25253.42,
  "timestamp": "2026-09-22 12:40:01"
}
```

Redis also stores a limited price history:

```text
market:history:<security_id>
```

Example:

```text
market:history:12345
```

This history is used by strategies such as EMA crossover.

---

# 8. Redis Pub/Sub

The project also publishes ticks through Redis Pub/Sub:

```text
market:ticks
```

Conceptually:

```text
Market Feed
     |
     +----> Redis latest tick
     |
     +----> Redis Pub/Sub
```

This allows multiple application components to consume market events.

---

# 9. Mock Market Feed

A mock market feed was implemented so the project can be developed without depending on live broker market data.

Run:

```bash
python manage.py mock_market
```

The mock feed:

- Generates NIFTY prices
- Changes price randomly
- Saves latest tick in Redis
- Saves price history
- Publishes market events
- Sends ticks through the Channels market router

Example:

```text
Mock market started...

NIFTY: 25253.42
NIFTY: 25249.87
NIFTY: 25252.11
```

This is the recommended development fallback when Dhan market-data access is unavailable.

---

# 10. Dhan Live Market Feed

The project also contains a real Dhan market-feed architecture.

Current design:

```text
Dhan WebSocket
       |
       v
DhanMarketFeed
       |
       v
DhanPacketParser
       |
       v
Internal Tick
       |
       v
MarketFeedManager
       |
       +----> Redis
       |
       +----> Channels
```

Dhan's v2 feed uses a WebSocket and binary market-data packets.

The project separates:

```text
Dhan protocol
```

from:

```text
Internal application tick format
```

This is important because the rest of the application should not depend directly on broker-specific packet formats.

### Important Dhan Access Note

Live Dhan market-data access depends on the user's Dhan API/data permissions.

The project previously encountered a Dhan access error indicating that the account did not have the required Data API access.

Therefore:

```text
Dhan Live Feed = Optional until account access is confirmed
Mock Feed      = Development fallback
```

Do not assume that possession of credentials automatically means live market-data access is enabled.

---

# 11. Dhan Binary Packet Parser

The live feed includes a packet parser:

```text
market/dhan_parser.py
```

Its purpose is to convert Dhan's binary feed packets into an internal representation:

```json
{
  "type": "ticker",
  "exchange_segment": "NSE_EQ",
  "security_id": "1333",
  "ltp": 25253.42,
  "timestamp": "..."
}
```

This normalization is important because strategies, Redis, WebSockets and the OMS should work with an application-level market-data structure rather than raw broker packets.

---

# 12. MarketFeedManager

The `MarketFeedManager` is the central market-data processing component.

Conceptually:

```text
Incoming Tick
     |
     v
MarketFeedManager
     |
     +----------------+
     |                |
     v                v
Latest Tick       Price History
Redis                 Redis
     |
     +----------------+
                      |
                      v
                 Pub/Sub
                      |
                      v
                  Channels
```

This gives the project a clean separation between:

- Data ingestion
- Data storage
- Data distribution
- Browser delivery
- Strategy processing

---

# 13. WebSocket Market Data

Django Channels is used for real-time market updates.

WebSocket endpoint:

```text
/ws/market/
```

The consumer joins:

```text
market_data
```

channel group.

Conceptually:

```text
Market Feed
     |
     v
Market Router
     |
     v
Channels Group
     |
     v
market_data
     |
     +------ Browser 1
     +------ Browser 2
     +------ Browser 3
```

The browser can receive:

```json
{
  "symbol": "NIFTY",
  "security_id": "12345",
  "ltp": 25253.42,
  "timestamp": "..."
}
```

---

# 14. REST Market API

The project also exposes latest tick data through REST.

Example:

```text
GET /api/market/ticks/<security_id>/
```

Example:

```text
GET /api/market/ticks/12345/
```

This gives two ways of consuming market data:

### REST

```text
GET
  |
  v
Latest Tick
```

### WebSocket

```text
Connection
  |
  v
Continuous Live Updates
```

---

# 15. Order Management System

The OMS is one of the most important components.

Its responsibility is to provide a broker-independent order lifecycle.

Architecture:

```text
Order Request
      |
      v
     OMS
      |
      +---- Validate
      |
      +---- Identify broker
      |
      +---- Select proxy
      |
      +---- Build broker payload
      |
      +---- Execute virtual/live mode
```

The OMS does not directly contain Dhan-specific logic.

Instead:

```text
OMS
 |
 +---- DhanAdapter
 |
 +---- ProxyService
```

---

# 16. Order Model

The `Order` model contains concepts such as:

```text
user
security_id
symbol
side
order_type
quantity
price
mode
status
broker_order_id
error_message
proxy_ip
proxy_port
created_at
updated_at
```

Order sides:

```text
BUY
SELL
```

Order types:

```text
MARKET
LIMIT
```

Trading modes:

```text
VIRTUAL
LIVE
```

Order statuses include:

```text
PENDING
PROXY_SELECTED
SENT_TO_DHAN
EXECUTED
FAILED
CANCELLED
```

---

# 17. Position Management

The project maintains a basic `Position` model.

Important concepts:

```text
user
security_id
symbol
quantity
average_price
realized_pnl
```

There is a unique relationship between:

```text
user + security_id
```

for the basic position implementation.

Virtual order execution updates positions.

---

# 18. Virtual Trading

Virtual trading is the primary safe trading mode during development.

Example:

```json
{
  "security_id": "12345",
  "symbol": "NIFTY",
  "side": "BUY",
  "quantity": 1,
  "order_type": "MARKET",
  "price": 0,
  "mode": "VIRTUAL"
}
```

Flow:

```text
API
 |
 v
OMS
 |
 v
Virtual Executor
 |
 +---- Order EXECUTED
 |
 +---- Position Updated
 |
 +---- P&L Updated
```

No real broker order is sent.

---

# 19. Live Trading Safety

Live trading is disabled by default.

Environment variable:

```env
LIVE_TRADING_ENABLED=False
```

Django setting:

```python
LIVE_TRADING_ENABLED = (
    os.getenv(
        "LIVE_TRADING_ENABLED",
        "False"
    ).lower() == "true"
)
```

The live executor should refuse live execution unless this flag is explicitly enabled.

This is intentional.

Never test a new strategy against a real broker accidentally.

---

# 20. Dhan Order Adapter

The project contains:

```text
orders/adapters/dhan.py
```

The adapter:

- Loads the user's active Dhan account
- Reads the Dhan access token
- Builds broker-specific order payloads
- Provides the Dhan API request layer
- Retrieves proxy configuration

A normalized application order is converted into a Dhan-specific payload.

Conceptually:

```text
Application Order
       |
       v
 DhanAdapter
       |
       v
Dhan Order Payload
       |
       v
Dhan API
```

---

# 21. Dhan Order Preview

A dry-run endpoint was also created.

Concept:

```text
/api/orders/dhan/preview/
```

It allows the application to inspect:

```text
broker
proxy
payload
```

without actually sending the order.

Example:

```json
{
  "dry_run": true,
  "broker": "DHAN",
  "proxy": {
    "host": "10.0.3.11",
    "port": 9000,
    "public_ip": "YOUR_EIP"
  },
  "payload": {}
}
```

This is useful for testing OMS behavior safely.

---

# 22. Proxy / EIP Architecture

One of the main learning goals of this project is dedicated broker egress.

The project models:

```text
EIPPool
ProxyAllocation
```

### EIPPool

Contains:

```text
public_ip
private_ip
is_allocated
created_at
```

### ProxyAllocation

Contains:

```text
user
eip
proxy_port
is_active
created_at
updated_at
```

The relationship is:

```text
User
 |
 v
ProxyAllocation
 |
 v
EIPPool
 |
 +---- Public EIP
 +---- Private IP
 +---- Proxy Port
```

---

# 23. Per-user Egress Design

The intended architecture is:

```text
User 1
   |
   v
Django OMS
   |
   v
Proxy EC2 :9000
   |
   v
HAProxy
   |
   v
Private IP 1
   |
   v
EIP 1
   |
   v
Dhan
```

Another user:

```text
User 2
   |
   v
Proxy EC2 :9001
   |
   v
HAProxy
   |
   v
Private IP 2
   |
   v
EIP 2
   |
   v
Dhan
```

This allows broker traffic to leave AWS through a user-specific Elastic IP.

---

# 24. Proxy Allocation

The allocator:

1. Checks whether the user already has an active allocation.
2. Finds an unused EIP.
3. Locks the EIP row using a database transaction.
4. Allocates a proxy port.
5. Creates `ProxyAllocation`.
6. Marks the EIP as allocated.

Default port range starts at:

```text
9000
```

Example:

```text
User 1 → EIP 1 → 9000
User 2 → EIP 2 → 9001
User 3 → EIP 3 → 9002
```

---

# 25. HAProxy

HAProxy runs on the proxy EC2.

The intended design is TCP pass-through.

Example architecture:

```text
App EC2
   |
   | 9000
   v
Proxy EC2
   |
   v
HAProxy
   |
   v
Dhan:443
```

Each backend uses the allocated private IP as its source address.

Conceptually:

```haproxy
backend user_1_backend
    mode tcp
    source 10.0.3.11
    server dhan <DHAN_HOST>:443
```

The actual Dhan hostname must be taken from current Dhan documentation/configuration rather than using a placeholder.

---

# 26. Important Proxy Networking Note

The HAProxy design implemented here is a **TCP forwarding design**, not an HTTP `CONNECT` proxy.

Therefore:

```text
requests.get(..., proxies=...)
```

must not automatically be assumed to work with this architecture.

A TCP pass-through HAProxy and an HTTP proxy are different things.

For production integration, the broker HTTPS traffic must be routed through the correct socket/network path so that:

```text
Django/Dhan client
       |
       v
Proxy EC2
       |
       v
HAProxy
       |
       v
User EIP
       |
       v
Dhan
```

remains valid.

---

# 27. Proxy Status API

A proxy status endpoint was added conceptually:

```text
/api/proxy/status/
```

It allows an authenticated user to inspect their active allocation.

Example information:

```text
active
host
port
public_ip
```

---

# 28. AWS Architecture

The target AWS architecture is:

```text
                         INTERNET
                            |
                            v
                    Internet Gateway
                            |
                     Public Subnet
                     10.0.1.0/24
                            |
              +-------------+-------------+
              |                           |
              v                           v
          App EC2                    Proxy EC2
       Django/Daphne                HAProxy
       Celery/Nginx                     |
              |                          |
              |                          +-- EIP 1
              |                          +-- EIP 2
              |                          +-- EIP 3
              |
              v
         Private Network
              |
        +-----+------+
        |            |
        v            v
       RDS        Redis
      MySQL
```

---

# 29. VPC Design

Recommended VPC:

```text
VPC
10.0.0.0/16
```

Subnets:

```text
Public App Subnet
10.0.1.0/24

Private Application/Data Subnet
10.0.2.0/24

Proxy Subnet
10.0.3.0/24
```

The exact subnet arrangement can be adjusted for the final AWS deployment, but the important separation is:

```text
Internet-facing application
        |
        v
Private database/cache
```

and:

```text
Application
    |
    v
Dedicated proxy/egress layer
```

---

# 30. AWS EC2 App Server

The App EC2 runs:

```text
Nginx
Django
Daphne
Celery
Market Feed
```

Typical application location:

```text
/var/www/quantpower
```

Virtual environment:

```text
/var/www/quantpower/venv
```

---

# 31. Nginx

Nginx sits in front of Django/Daphne.

HTTP path:

```text
Internet
   |
   v
Nginx :80/:443
   |
   v
Daphne :8000
   |
   v
Django
```

WebSocket path:

```text
Browser
   |
   v
Nginx
   |
   v
/ws/
   |
   v
Daphne
   |
   v
Channels
```

Nginx therefore handles:

- HTTP reverse proxy
- WebSocket reverse proxy
- Static files
- TLS termination when HTTPS is configured

---

# 32. Daphne

Daphne serves the Django ASGI application.

Systemd service:

```text
quantpower-daphne.service
```

Conceptual command:

```bash
daphne \
    -b 127.0.0.1 \
    -p 8000 \
    config.asgi:application
```

This supports both:

```text
HTTP
```

and:

```text
WebSocket
```

---

# 33. Celery

Celery is used for background jobs.

Redis is the broker/result backend.

Conceptually:

```text
Django
   |
   | task
   v
Redis
   |
   v
Celery Worker
   |
   v
Background Job
```

Current project uses Celery for strategy/background processing.

A production service can be:

```text
quantpower-celery.service
```

---

# 34. Market Feed Service

The live Dhan feed can run as its own systemd service:

```text
quantpower-market.service
```

Conceptually:

```text
systemd
   |
   v
manage.py dhan_market
   |
   v
Dhan WebSocket
   |
   v
Redis
```

If live Dhan data is unavailable:

```text
manage.py mock_market
```

can be used for development.

---

# 35. Database

The project is designed for MySQL in production.

AWS target:

```text
Amazon RDS MySQL
```

Application flow:

```text
Django
   |
   v
RDS MySQL
```

Database should not be publicly accessible.

Security group should allow MySQL traffic only from the application security group.

---

# 36. Redis

Redis handles:

- Latest market ticks
- Price history
- Pub/Sub
- Django Channels
- Celery broker
- Celery results

Target AWS deployment:

```text
Amazon ElastiCache for Redis
```

or another private Redis deployment appropriate for the environment.

Redis should not be exposed publicly.

---

# 37. AWS Security Groups

Recommended security model:

### App EC2

Allow:

```text
22   → Admin IP only
80   → Internet
443  → Internet
```

### Proxy EC2

Allow:

```text
22           → Admin IP only
9000-9999    → App EC2 security group only
```

### RDS

Allow:

```text
3306 → App EC2 security group only
```

### Redis

Allow:

```text
6379 → App EC2 security group only
```

Do not expose:

```text
3306
6379
9000-9999
```

to:

```text
0.0.0.0/0
```

---

# 38. Environment Configuration

Example:

```env
DEBUG=False

SECRET_KEY=change-this

ALLOWED_HOSTS=example.com,www.example.com

DB_NAME=quantpower
DB_USER=quantpower
DB_PASSWORD=...
DB_HOST=...
DB_PORT=3306

REDIS_URL=redis://...

DHAN_CLIENT_ID=...
DHAN_ACCESS_TOKEN=...

LIVE_TRADING_ENABLED=False
```

Never commit `.env`.

`.gitignore` includes:

```text
.env
venv/
__pycache__/
*.pyc
db.sqlite3
```

---

# 39. Django Settings Architecture

The project uses environment variables for deployment configuration.

Important settings include:

```python
ASGI_APPLICATION = "config.asgi.application"
```

Redis:

```python
REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://127.0.0.1:6379/0",
)
```

Channels:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND":
            "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}
```

Celery:

```python
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
```

---

# 40. ASGI Architecture

The project uses:

```text
config/asgi.py
```

with:

```text
HTTP
  ↓
Django ASGI

WebSocket
  ↓
AuthMiddlewareStack
  ↓
URLRouter
  ↓
MarketConsumer
```

This allows one ASGI application to support both REST/API traffic and WebSockets.

---

# 41. Strategy Engine

The first implemented strategy is:

```text
EMA Crossover
```

Strategy types currently modeled include:

```text
EMA_CROSSOVER
RSI
```

The EMA implementation uses:

```text
Fast EMA
Slow EMA
```

Example:

```text
EMA 9
EMA 21
```

Basic logic:

```text
EMA9 > EMA21
      ↓
     BUY

EMA9 < EMA21
      ↓
     SELL

Insufficient data
      ↓
     HOLD
```

---

# 42. Strategy Model

A strategy contains:

```text
user
name
strategy_type
security_id
symbol
quantity
fast_period
slow_period
is_active
created_at
updated_at
```

Example:

```json
{
  "name": "NIFTY EMA Test",
  "strategy_type": "EMA_CROSSOVER",
  "security_id": "12345",
  "symbol": "NIFTY",
  "quantity": 1,
  "fast_period": 9,
  "slow_period": 21,
  "is_active": true
}
```

---

# 43. Strategy Signals

Every evaluation can create a `StrategySignal`.

Signal types:

```text
BUY
SELL
HOLD
```

A signal stores:

```text
strategy
signal
price
reason
created_at
```

Example:

```json
{
  "signal": "BUY",
  "price": "25265.40",
  "reason": "EMA9 above EMA21"
}
```

---

# 44. Strategy Runner

The Strategy Runner connects:

```text
Strategy
   |
   v
Redis Price History
   |
   v
Indicator
   |
   v
Signal
   |
   v
OMS
```

For development, strategy orders are forced to:

```text
VIRTUAL
```

---

# 45. Celery Strategy Execution

A Celery task was created:

```text
run_strategy(strategy_id)
```

Conceptually:

```text
Celery
   |
   v
Strategy
   |
   v
StrategyRunner
   |
   v
Signal
   |
   v
OMS
```

This allows strategy evaluation to happen outside the web request.

---

# 46. Strategy APIs

Main concepts:

```text
GET/POST /api/strategies/
```

Run:

```text
POST /api/strategies/<id>/run/
```

Signals:

```text
GET /api/strategies/<id>/signals/
```

---

# 47. Current Project Structure

The intended structure is:

```text
quantpower-mini/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── celery.py
│   └── routing.py
│
├── users/
│
├── dhan/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── services.py
│
├── market/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── routing.py
│   ├── consumers.py
│   ├── router.py
│   ├── redis_service.py
│   ├── feed_manager.py
│   ├── dhan_feed.py
│   ├── dhan_parser.py
│   └── management/
│       └── commands/
│           ├── mock_market.py
│           └── dhan_market.py
│
├── orders/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── oms.py
│   └── adapters/
│       └── dhan.py
│
├── strategies/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── indicators.py
│   ├── engine.py
│   ├── services.py
│   ├── runner.py
│   └── tasks.py
│
├── backtest/
│
├── proxy/
│   ├── models.py
│   ├── allocator.py
│   ├── services.py
│   └── generate_haproxy.py
│
├── proxy_deploy/
│   ├── generate_haproxy.py
│   ├── allocations.json
│   ├── deployed.json
│   └── brokers.json
│
├── templates/
├── static/
│
├── manage.py
├── requirements.txt
├── .env
└── .gitignore
```

---

# 48. Important Runtime Services

On the final App EC2, the major processes are:

```text
quantpower-daphne
quantpower-celery
quantpower-market
nginx
```

On Proxy EC2:

```text
haproxy
```

Infrastructure:

```text
RDS MySQL
Redis
Elastic IPs
```

---

# 49. Development Commands

Create environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

Run checks:

```bash
python manage.py check
```

Migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create admin:

```bash
python manage.py createsuperuser
```

Run Django:

```bash
python manage.py runserver
```

Run mock market:

```bash
python manage.py mock_market
```

Run Dhan market feed:

```bash
python manage.py dhan_market
```

Run Celery:

```bash
celery -A config worker -l info
```

---

# 50. API Overview

Current API concepts:

```text
Authentication
────────────────────────
POST /api/auth/login/
POST /api/auth/refresh/


Dhan
────────────────────────
GET/POST /api/dhan/account/


Market
────────────────────────
GET /api/market/instruments/
GET /api/market/ticks/<security_id>/


Orders
────────────────────────
GET  /api/orders/
POST /api/orders/create/
GET  /api/orders/positions/
POST /api/orders/dhan/preview/


Proxy
────────────────────────
GET /api/proxy/status/


Strategies
────────────────────────
GET  /api/strategies/
POST /api/strategies/
POST /api/strategies/<id>/run/
GET  /api/strategies/<id>/signals/


WebSocket
────────────────────────
/ws/market/
```

Exact routes may evolve as the project continues.

---

# 51. Backtesting — Planned / Next Major Module

A `backtest` Django application has been created for the next major stage.

The planned architecture is:

```text
Historical Data
      |
      v
Backtest Engine
      |
      v
Strategy
      |
      v
Signals
      |
      v
Virtual Execution
      |
      v
Trades
      |
      v
Performance Metrics
```

Planned metrics include:

```text
Initial Capital
Final Capital
Total P&L
Return %
Win Rate
Max Drawdown
Total Trades
Equity Curve
```

The important design goal is:

```text
Same Strategy Logic
       |
       +------ Live/Simulation
       |
       +------ Backtest
```

so strategy logic does not need to be duplicated.

---

# 52. What We Are Intentionally NOT Building Yet

This is a mini version of the larger platform.

The following are intentionally excluded or simplified:

- Multiple brokers
- Complex membership/subscription system
- CRM
- Blog
- Chatbot
- Complex option Greeks
- Advanced option-chain engine
- TradingView data infrastructure
- Complex alert system
- Multiple bot families
- Large-scale analytics
- Multi-region infrastructure
- Full high-availability architecture
- Complex billing/payment system
- Nine broker adapters

The only broker currently targeted is:

```text
Dhan
```

---

# 53. Relationship to the Larger QuantPower Architecture

The original QuantPower-style architecture contains significantly more functionality, including:

- Multiple broker adapters
- Market feeds
- OMS
- Bots
- WebSockets
- Redis
- Celery/cron jobs
- Dedicated EIP proxy architecture
- User broker connections
- Option-chain data
- Trading strategies
- Additional application modules

This mini project preserves the important architectural concepts while reducing the feature count.

The objective is:

```text
Understand architecture first
          ↓
Implement smaller version
          ↓
Deploy on AWS
          ↓
Test each component
          ↓
Add complexity gradually
```

---

# 54. Security Principles

Never commit:

```text
.env
Dhan access tokens
API secrets
Database passwords
AWS credentials
Private keys
```

Use:

```text
Environment variables
AWS Secrets Manager
SSM Parameter Store
```

where appropriate for production.

Never expose:

```text
MySQL
Redis
HAProxy user ports
```

directly to the public internet.

Keep:

```text
LIVE_TRADING_ENABLED=False
```

during development.

---

# 55. Important Production Considerations

Before real trading, the following still require hardening:

### Authentication

- Token expiry handling
- Refresh-token security
- Session/device management
- Rate limiting

### Orders

- Idempotency
- Duplicate-order prevention
- Broker acknowledgement handling
- Order status synchronization
- Cancellation handling
- Retry policies
- Partial fills

### Market Data

- Reconnect handling
- Packet validation
- Subscription recovery
- Feed health monitoring
- Stale-data detection

### Strategy

- Duplicate signal prevention
- Position-aware signals
- Risk limits
- Max daily loss
- Quantity validation
- Market-hours handling

### Proxy

- EIP health monitoring
- HAProxy health checks
- Allocation recovery
- Port management
- Configuration deployment
- Failover

### Infrastructure

- HTTPS
- Backups
- Monitoring
- Logging
- Alerts
- IAM
- Secret management
- Database backups
- Redis authentication/TLS
- EC2 patching

---

# 56. Recommended Production Order Flow

The intended hardened flow should eventually become:

```text
Client
  |
  v
Authentication
  |
  v
Order Validation
  |
  v
Risk Validation
  |
  v
Idempotency Check
  |
  v
OMS
  |
  v
Proxy Selection
  |
  v
Dhan Adapter
  |
  v
HAProxy
  |
  v
User EIP
  |
  v
Dhan
  |
  v
Broker Order ID
  |
  v
Order Status
  |
  v
Database
```

---

# 57. Development Philosophy

The project is intentionally being built in phases.

### Phase 1

Project foundation

### Phase 2

Users + Dhan account

### Phase 3

Instruments + market data

### Phase 4

WebSocket

### Phase 5

Redis + market router

### Phase 6

OMS

### Phase 7

Dhan adapter

### Phase 8

Proxy + EIP

### Phase 9

AWS infrastructure

### Phase 10

Django/Daphne deployment

### Phase 11

Proxy EC2 + HAProxy

### Phase 12

OMS → Proxy integration

### Phase 13

Order lifecycle

### Phase 14

Market-data pipeline

### Phase 15

Real Dhan market feed

### Phase 16

Strategy engine

### Phase 17

Backtesting

Future phases can add:

```text
Risk Engine
Order status synchronization
Advanced strategies
Frontend dashboard
Monitoring
Production hardening
```

---

# 58. Complete High-Level Architecture

```text
                           INTERNET
                              |
                              v
                         Route 53 / DNS
                              |
                              v
                         Nginx / HTTPS
                              |
                    +---------+---------+
                    |                   |
                    v                   v
               REST API             WebSocket
                    |                   |
                    v                   v
                 Django              Daphne
                    |
       +------------+-------------+
       |            |             |
       v            v             v
      OMS        Strategy       Dhan Account
       |            |
       |            v
       |         Redis History
       |
       v
 Dhan Adapter
       |
       v
 Proxy Allocation
       |
       v
   Proxy EC2
       |
       v
    HAProxy
       |
       +-------- EIP 1
       +-------- EIP 2
       +-------- EIP 3
       |
       v
      Dhan


MARKET DATA:

      Dhan
       |
       v
Dhan WebSocket
       |
       v
Packet Parser
       |
       v
MarketFeedManager
       |
       +----------> Redis
       |
       +----------> Channels
                       |
                       v
                   WebSocket
                       |
                       v
                    Browser


BACKGROUND:

      Django
        |
        v
      Redis
        |
        v
     Celery
        |
        +---- Strategy Jobs
        +---- Background Jobs
```

---

# 59. Final Learning Outcome

After completing this project, you should understand how these components work together:

```text
Django
DRF
JWT
Dhan API
Market Data
WebSockets
Redis
Pub/Sub
Celery
OMS
Broker Adapter
Virtual Trading
Strategies
Backtesting
HAProxy
Elastic IP
EC2
RDS
Nginx
Daphne
systemd
AWS Networking
Security Groups
VPC
```

More importantly, the project demonstrates the separation between:

```text
DATA PLANE

Dhan
 ↓
Market Feed
 ↓
Redis
 ↓
WebSocket
 ↓
Browser


TRADING PLANE

User / Strategy
 ↓
OMS
 ↓
Broker Adapter
 ↓
Proxy
 ↓
EIP
 ↓
Dhan


CONTROL / BACKGROUND PLANE

Django
 ↓
Celery
 ↓
Strategies / Jobs
```

This separation is the core architectural idea behind the project.

---

# 60. Current Status

```text
┌───────────────────────────────────────────┐
│          QUANTPOWER MINI STATUS           │
├───────────────────────────────────────────┤
│ Django / DRF                    ✅         │
│ JWT Authentication              ✅         │
│ Dhan Account                    ✅         │
│ Instrument Model                ✅         │
│ Redis                           ✅         │
│ WebSockets                      ✅         │
│ Mock Market Feed                ✅         │
│ Dhan Market Feed Architecture   ✅/🔧      │
│ OMS                             ✅         │
│ Virtual Orders                  ✅         │
│ Positions                       ✅         │
│ Dhan Adapter                    ✅         │
│ Proxy Allocation                ✅         │
│ HAProxy Architecture            ✅         │
│ AWS Architecture                ✅         │
│ Nginx                           ✅         │
│ Daphne                          ✅         │
│ Celery                          ✅         │
│ EMA Strategy                    ✅         │
│ Strategy Signals                ✅         │
│ Backtesting                     🔧 NEXT    │
│ Risk Engine                     🔜          │
│ Production Hardening            🔜          │
│ Live Trading                    🔒 OFF      │
└───────────────────────────────────────────┘
```

---

## Disclaimer

This project is for software engineering, architecture, and trading-system development practice. Market data, broker APIs, order execution, and regulatory requirements can change. Live trading should remain disabled until the complete system has been independently tested and the relevant broker/account permissions and safeguards have been verified.
