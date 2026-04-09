# Arbitrage-1 — Sports Betting Arbitrage System

A Python-based arbitrage detection and auto-firing system that monitors **DraftKings, FanDuel, BetMGM, and Caesars** in real time, flags cross-book profit opportunities, sends **Discord alerts**, displays them on a **live web dashboard**, and optionally **auto-fires bets** via browser automation.

---

## How It Works

Sports books occasionally disagree on the true probability of an outcome. When the combined implied probabilities of all outcomes in a market across different books sum to **less than 100%**, a guaranteed profit exists regardless of the result — this is an arbitrage opportunity.

### 2-Way Market (Moneyline / Spread / Total)
```
ips = 1/best_odds_outcome_A + 1/best_odds_outcome_B

if ips < 1.0:
    profit_margin = (1 / ips) - 1
    stake_A = total_bankroll * (1/odds_A) / ips
    stake_B = total_bankroll * (1/odds_B) / ips
```

### 3-Way Market (Soccer with Draw)
```
ips = 1/home_odds + 1/draw_odds + 1/away_odds

if ips < 1.0: arb exists
```

---

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ (fully async) |
| Browser automation | Playwright + playwright-stealth |
| Web framework | FastAPI + Jinja2 + WebSocket |
| Alerts | Discord webhook (embeds) |
| Event matching | rapidfuzz (fuzzy team name matching) |
| Logging | structlog |
| Config | python-dotenv + dataclasses |

---

## Project Structure

```
Arbitrage-1/
├── .env.example                     # All config keys with defaults
├── .gitignore
├── requirements.txt
├── config.py                        # load_config() → Config dataclass
├── main.py                          # asyncio entrypoint — wires everything together
│
├── models/
│   ├── odds.py                      # OddsLine, MarketSnapshot, OddsFormat, MarketType
│   ├── arb.py                       # ArbOpportunity, ArbLeg
│   └── event.py                     # NormalizedEvent
│
├── scraper/
│   ├── base_scraper.py              # BaseScraper ABC — login, scrape_all, anti-bot helpers
│   ├── session_manager.py           # One BrowserContext per book, persistent storage state
│   ├── draftkings.py
│   ├── fanduel.py
│   ├── betmgm.py
│   └── caesars.py
│
├── normalizer/
│   ├── odds_converter.py            # American / Fractional / Decimal → Decimal
│   └── event_normalizer.py          # Canonical team names + deterministic event keys
│
├── matcher/
│   └── event_matcher.py             # Groups OddsLines into cross-book MarketSnapshots
│
├── detector/
│   └── arb_detector.py              # 2-way + 3-way arb math, stake calculator
│
├── alerts/
│   ├── discord.py                   # Discord embed webhook dispatcher
│   └── alert_manager.py             # Deduplication + per-market cooldown
│
├── autofire/
│   ├── base_bettor.py               # BaseBettor ABC — place_bet, human typing, delays
│   ├── draftkings_bettor.py
│   ├── fanduel_bettor.py
│   ├── betmgm_bettor.py
│   └── caesars_bettor.py
│
├── dashboard/
│   ├── app.py                       # FastAPI app factory
│   ├── routes.py                    # GET /, WS /ws, GET /api/opportunities
│   ├── state.py                     # DashboardState — asyncio.Queue pub/sub
│   ├── templates/
│   │   └── index.html               # Jinja2 — live arb opportunity table
│   └── static/
│       ├── main.js                  # WebSocket client, DOM updates
│       └── style.css
│
├── utils/
│   ├── logger.py                    # Structured logging config
│   └── retry.py                     # Exponential backoff decorator
│
└── sessions/                        # gitignored — Playwright storage states per book
```

---

## Data Flow

```
[Playwright x4 books — concurrent asyncio.gather()]
           │
           │  page.on("response") XHR interception → raw JSON
           ▼
   [BaseScraper.scrape_all()]
           │
           │  OddsLine[] with raw_odds string
           ▼
   [OddsConverter]  →  decimal_odds normalized
   [EventNormalizer]  →  canonical event_id key
           │
           ▼
   [EventMatcher.group_by_market()]
           │
           │  MarketSnapshot[]  (same market, lines from 2+ books)
           ▼
   [ArbDetector.detect()]
           │
           │  ArbOpportunity | None
           ▼
      ┌────┴──────────────────────────────────────────┐
      │             (if arb found)                    │
      ▼                    ▼                          ▼
[AlertManager]    [DashboardState]            [if autofire_enabled]
      │            .publish_opportunity()             │
      ▼                    │                          ▼
[Discord Webhook]    [WebSocket broadcast]   [BaseBettor.place_bet()
  (embed)           → browser dashboard      per leg, concurrent]
```

---

## Key Components

### Scraping Strategy
Rather than fragile DOM scraping, the scrapers use **Playwright's `page.on("response")` network interception** to capture the internal REST/GraphQL API calls that each book's SPA makes. This approach:
- Is faster than DOM parsing
- Survives frontend redesigns
- Returns clean structured JSON directly

### Event Matching (Cross-Book)
Matching the same game across 4 different books is the hardest practical problem. A three-tier strategy is used:

| Tier | Method | Handles |
|---|---|---|
| 1 | Exact canonical key | ~85% of cases — `sport::teamA__teamB::date` |
| 2 | `rapidfuzz.token_sort_ratio >= 85` | Name variations — "LA Clippers" vs "Los Angeles Clippers" |
| 3 | Start time within 30-minute window | Prevents cross-day collisions |

Spread/total markets additionally require an **exact line value match** (e.g., `-3.5 ≠ -3.0`). Any OddsLine older than **2 minutes** is rejected as stale.

### Session Management
- One `BrowserContext` per book with cookies/localStorage persisted to `sessions/{book}_state.json`
- Login only runs on first launch or when a mid-scrape redirect to the login page is detected
- `playwright-stealth` applied to each context to remove Playwright fingerprints
- Random viewport jitter, realistic user agents, and human-like typing delays (character-by-character) for anti-bot evasion
- CAPTCHA detection saves a screenshot, backs off with exponential retry, and sends a Discord alert for human intervention

### Discord Alerts
Each opportunity fires a rich **Discord embed** containing:
- Event name, sport, and market type
- Each leg: book · outcome · odds · stake amount
- Profit margin % and guaranteed profit in dollars
- Timestamp detected

An `AlertManager` deduplication layer enforces a per-market cooldown (default 5 minutes) to prevent spam.

### Live Dashboard
```
GET  /                    →  Jinja2-rendered table (initial state snapshot)
WS   /ws                  →  Real-time push updates via WebSocket
GET  /api/opportunities   →  REST JSON (polling fallback)
GET  /api/history         →  Recent arb history
```

WebSocket messages follow this shape:
```json
{
  "type": "opportunity_added" | "opportunity_expired" | "bet_fired",
  "data": { ...ArbOpportunity... }
}
```

Frontend uses vanilla JS + WebSocket — no build step, no framework.

### Auto-Fire Safety
Auto-fire is **disabled by default** and has its own second confirmation threshold higher than the detection threshold. Before clicking confirm on any bet slip, the bettor **re-reads the current odds** and aborts the leg if they have moved past the arb threshold. All legs fire concurrently via `asyncio.gather` to minimize timing gap between books.

---

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```env
# Scraping
SCRAPE_INTERVAL_SECONDS=30
HEADLESS=true
USE_STEALTH=true

# Arb detection
MIN_PROFIT_MARGIN=0.01          # 1% — flag threshold
TOTAL_BANKROLL=10000
MAX_STAKE_PER_LEG=500

# Alerts
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
ALERT_COOLDOWN_SECONDS=300

# Auto-fire (keep false until thoroughly tested)
AUTOFIRE_ENABLED=false
AUTOFIRE_CONFIRM_THRESHOLD=0.02  # 2% — fire threshold (higher than flag)

# Sportsbook credentials
DRAFTKINGS_USERNAME=
DRAFTKINGS_PASSWORD=
FANDUEL_USERNAME=
FANDUEL_PASSWORD=
BETMGM_USERNAME=
BETMGM_PASSWORD=
CAESARS_USERNAME=
CAESARS_PASSWORD=

# Dashboard
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8000
```

---

## Installation

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browser
playwright install chromium

# 4. Copy and fill in your config
cp .env.example .env

# 5. Run
python main.py
```

Dashboard will be available at `http://localhost:8000`

---

## Dependencies

```
playwright==1.43.0
playwright-stealth==1.0.6
fastapi==0.111.0
uvicorn[standard]==0.29.0
jinja2==3.1.4
websockets==12.0
aiohttp==3.9.5
rapidfuzz==3.9.3
python-dotenv==1.0.1
pydantic==2.7.1
numpy==1.26.4
structlog==24.1.0
pytest==8.2.0
pytest-asyncio==0.23.7
pytest-mock==3.14.0
```

---

## Build Phases

| Phase | Components | Milestone |
|---|---|---|
| 1 | `config.py`, `models/`, `normalizer/` | Raw odds string → correct decimal odds + canonical event key |
| 2 | `detector/arb_detector.py`, `matcher/` | Mock OddsLines → correct ArbOpportunity with verified stakes |
| 3 | `dashboard/` (full) | Fake arbs visible live in browser via WebSocket |
| 4 | `alerts/discord.py` + `alert_manager.py` | Fake arb triggers Discord embed with correct data |
| 5 | `scraper/draftkings.py` + `session_manager.py` | Real DraftKings odds flowing through full pipeline |
| 6 | `scraper/fanduel.py`, `betmgm.py`, `caesars.py` | All 4 books scraping live |
| 7 | `main.py` full integration | End-to-end real arbs appearing in dashboard + Discord |
| 8 | `autofire/` (dry-run first) | Bets logging correctly in dry-run before enabling live fire |

---

## Testing

```bash
# Unit tests (normalizer + detector are pure functions — fully testable without a browser)
pytest tests/

# Scraper smoke test (prints live OddsLine objects)
python -m scraper.draftkings --debug

# Dashboard smoke test (pushes fake arb, verify WebSocket update)
python -m dashboard.state --test

# Auto-fire dry run (logs stake amounts without placing bets)
AUTOFIRE_ENABLED=true DRY_RUN=true python main.py
```

---

## Risks and Disclaimers

> **Terms of Service**: Automated scraping and betting is prohibited by the terms of service of DraftKings, FanDuel, BetMGM, and Caesars. Use of this system may result in account suspension or banning.

> **Odds movement**: True arbitrage windows are extremely short (seconds to minutes). By the time auto-fire navigates to a bet slip, odds may have moved. The system re-verifies odds before confirming every bet to prevent guaranteed losses from stale opportunities.

> **This project is for educational purposes.** The architecture demonstrates async scraping, cross-source data normalization, real-time dashboards, and browser automation techniques.
