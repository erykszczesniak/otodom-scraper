# Otodom Scraper

A web scraper for rental listings on Otodom.pl (Warsaw), with a React dashboard and notifications via Telegram and email.

<!-- screenshot -->

## Requirements

- Docker + Docker Compose

## Quickstart

```bash
git clone https://github.com/erykszczesniak/otodom-scraper.git
cd otodom-scraper
cp .env.example .env   # fill in tokens
docker compose up --build
# backend: http://localhost:8000/docs
# frontend: http://localhost:3000
```

## Configuration

| Variable | Description | Default |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | — |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | — |
| `SMTP_HOST` | SMTP server host | — |
| `SMTP_PORT` | SMTP port | 587 |
| `SMTP_USER` | SMTP login | — |
| `SMTP_PASSWORD` | SMTP password | — |
| `NOTIFY_EMAIL` | Notification email address | — |
| `SCRAPE_INTERVAL_HOURS` | Scrape interval in hours | 6 |

## Data Formats

Every listings endpoint supports `?format=json|xml|csv`.

```bash
# JSON (default)
curl "http://localhost:8000/api/listings?format=json" | head -20

# XML
curl "http://localhost:8000/api/listings?format=xml" | head -20

# CSV (export)
curl -o export.csv "http://localhost:8000/api/listings?format=csv"
```

## Alerts

Copy `data/alerts.json.example` to `data/alerts.json` and edit the criteria:

```json
[
  {
    "name": "Mokotow with bathtub",
    "price_max": 4000,
    "district": "Mokotow",
    "has_bathtub": true,
    "metro_max_min": 10
  }
]
```

After each scrape, new listings matching alert criteria will trigger Telegram and email notifications.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/listings` | List listings with filters and pagination |
| `GET` | `/api/listings/{id}` | Listing details with price history |
| `GET` | `/api/listings/{id}/price-history` | Price history for a listing |
| `GET` | `/api/listings/stats/overview` | Aggregate statistics |
| `POST` | `/api/scrape` | Trigger manual scrape |
| `GET` | `/api/scrape/status` | Last 10 scrape runs |
| `POST` | `/api/scrape/enrich` | Trigger detail page enrichment |
| `GET` | `/api/health` | Health check |

### Filter Parameters (`GET /api/listings`)

`price_min`, `price_max`, `area_min`, `area_max`, `rooms` (repeatable), `district`, `has_bathtub`, `pets_allowed`, `agency_fee`, `metro_max_min`, `center_max_min`, `deposit_max`, `furnished`, `sort_by`, `sort_dir`, `page`, `per_page`, `format`

## Project Structure

```
otodom-scraper/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + scheduler
│   │   ├── config.py            # Environment variables
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   ├── models.py            # Listing, PriceHistory, ScrapeRun
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── format_utils.py      # JSON/XML/CSV formatters
│   │   ├── scraper/
│   │   │   ├── otodom.py        # Otodom scraper (httpx + BS4)
│   │   │   └── enricher.py      # Detail page enrichment
│   │   ├── routers/
│   │   │   ├── listings.py      # CRUD + filters + export
│   │   │   └── scrape.py        # Trigger + status
│   │   └── notifications/
│   │       ├── alerts.py        # Matching logic
│   │       ├── email.py         # SMTP (aiosmtplib)
│   │       └── telegram.py      # Telegram Bot API
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Dashboard layout
│   │   ├── api.js               # API client
│   │   ├── components/          # FilterPanel, ListingCard, Modal, etc.
│   │   └── hooks/               # TanStack Query hooks
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
├── data/                        # SQLite DB + alerts.json
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## License

MIT
