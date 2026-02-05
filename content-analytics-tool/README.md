# Content Analytics Tool

A comprehensive social media analytics platform for tracking YouTube and Instagram performance.

## Features

- **YouTube Analytics**: Track subscriber growth, video performance, and comment sentiment
- **Instagram Analytics**: Monitor follower growth, engagement rates, and post performance
- **ML Predictions**: Prophet-based forecasting for growth projections
- **Dark Mode Dashboard**: Beautiful, modern Streamlit interface

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Launch with Docker

```bash
# Start all services (PostgreSQL, Redis, Streamlit app)
docker-compose up -d --build

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

Access the dashboard at **http://localhost:8501**

### Initialize Database

The database tables are automatically created when the app starts. For manual initialization:

```bash
docker-compose exec app python scripts/init_db.py
```

## Configuration

Edit `.env` file to add your API keys:

```
YOUTUBE_API_KEY=your_youtube_api_key
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
```

## Project Structure

```
content-analytics-tool/
├── app/                  # Streamlit dashboard
├── src/
│   ├── api/             # YouTube & Instagram API clients
│   ├── database/        # SQLAlchemy models & queries
│   ├── analytics/       # Engagement metrics & sentiment
│   └── ml/              # Prophet forecasting
├── data/                # Data storage
├── scripts/             # Utility scripts
└── docker-compose.yml   # Docker configuration
```

## Tech Stack

- **Frontend**: Streamlit, Plotly
- **Backend**: Python, SQLAlchemy
- **Database**: PostgreSQL
- **Cache**: Redis
- **ML**: Prophet, scikit-learn
- **APIs**: YouTube Data API v3, Instagram Graph API
