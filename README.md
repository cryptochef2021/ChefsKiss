# StayAgg — Rental Aggregator Platform

A platform that aggregates rental listings from Airbnb, Booking.com, Agoda, local Vietnamese/Thai sites, and other regional platforms into a single searchable interface. Designed for digital nomads and long-term travelers who want to find the best deals — especially in Southeast Asia where local sites beat Airbnb pricing significantly.

## The Problem

- **Fragmented listings**: Great long-term rental deals exist on local sites (e.g., Batdongsan.com.vn, DDProperty, Renthub.in.th) but are hard to discover.
- **Language barriers**: Local sites are often only in Vietnamese, Thai, etc. with no reliable translation.
- **Contact friction**: Many local/Asian platforms require a local phone number to message hosts.
- **No unified reviews**: A host may have great reviews on Airbnb but you'd never see them when finding their listing on a local site.
- **Calendar fragmentation**: Hosts list on multiple platforms but availability isn't synced.

## The Solution

StayAgg provides:

1. **Unified Search** — Search across Airbnb, Booking.com, Agoda, local sites, and Facebook groups from one interface.
2. **Cross-Platform Reviews** — Aggregate and display host reputation from all platforms where they list.
3. **Auto-Translation** — Translate listings and enable messaging in any language.
4. **Unified Messaging** — Contact hosts on local platforms without needing a local phone number.
5. **Calendar Sync** — iCal-based calendar integration so hosts can sync availability across platforms.
6. **Price Comparison** — Side-by-side pricing for the same or similar properties across platforms.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│   Frontend   │────▶│   API Gateway    │────▶│  PostgreSQL  │
│  React + TS  │     │  FastAPI/Python  │     │              │
└─────────────┘     └──────┬───────────┘     └──────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌────────────┐ ┌────────┐ ┌──────────┐
       │  Scrapers/  │ │ iCal   │ │ Translat.│
       │  Adapters   │ │ Sync   │ │ Service  │
       └────────────┘ └────────┘ └──────────┘
```

### Tech Stack

| Layer        | Technology                          |
|-------------|--------------------------------------|
| Frontend    | React, TypeScript, Tailwind CSS      |
| Backend     | Python, FastAPI, Celery              |
| Database    | PostgreSQL, Redis                    |
| Scraping    | Playwright, BeautifulSoup            |
| Translation | DeepL API / Google Translate API     |
| Calendar    | iCal protocol (RFC 5545)             |
| Deployment  | Docker, Docker Compose               |

## Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/             # API route handlers
│   │   ├── core/            # Config, security, deps
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── scrapers/        # Platform-specific scrapers
│   │   └── workers/         # Celery async tasks
│   ├── alembic/             # DB migrations
│   ├── tests/
│   └── requirements.txt
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15+

### Development Setup

```bash
# Clone the repo
git clone <repo-url> && cd stayagg

# Start infrastructure
docker-compose up -d postgres redis

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Business Model

- **Free for travelers** — no booking fees (undercutting Airbnb's 14-20% guest+host fees)
- **Freemium for hosts** — free listing, paid for calendar sync & analytics
- **Lead generation** — connect property managers with guests
- Revenue grows with listing volume; hosts lose nothing by being on the platform

## Feasibility Notes

- **Calendar sync**: iCal export/import is widely supported (Airbnb, VRBO, Booking.com all export iCal feeds). No proprietary API needed.
- **Scraping**: Legal gray area — we aggregate publicly available data. Terms of service vary by platform.
- **Translation**: DeepL and Google Translate APIs are mature and affordable for Vietnamese/Thai/etc.
- **Local contact**: We can proxy messages via local phone numbers (Twilio/local SMS gateways) or use platform APIs where available.

## License

MIT
