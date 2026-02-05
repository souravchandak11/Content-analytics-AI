# Content Analytics Platform 📊

A production-ready analytics platform for YouTube and Instagram creators. Track performance, predict viral content, and optimize your content strategy with ML-powered insights.

## Features

- **📈 Real-time Analytics** - Track views, engagement, subscribers, and growth
- **🤖 ML Predictions** - Predict viral potential of content before posting
- **📊 Time-series Forecasting** - Prophet-based subscriber and view predictions
- **💬 Sentiment Analysis** - Understand audience feedback from comments
- **📉 Trend Analysis** - Identify patterns and optimize posting times
- **🔄 Automated Data Collection** - Scheduled ETL pipeline for continuous data updates

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | FastAPI, SQLAlchemy, PostgreSQL, Redis |
| **Frontend** | Streamlit, Plotly |
| **ML/Analytics** | Scikit-learn, Prophet, NLTK, Pandas, NumPy |
| **APIs** | YouTube Data API v3, Instagram Graph API |
| **Infrastructure** | Docker, Docker Compose |

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis (optional, for rate limiting)
- Docker & Docker Compose (recommended)

### Installation

1. **Clone and setup environment**
   ```bash
   cd "Content Analytics"
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   copy .env.example .env
   # Edit .env with your API keys and database credentials
   ```

3. **Start with Docker (recommended)**
   ```bash
   docker-compose up -d
   ```

   Or start services individually:
   ```bash
   # Start database
   docker-compose up -d postgres redis
   
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Run migrations
   python -c "from src.database import init_database; init_database()"
   
   # Start API server
   uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
   
   # Start dashboard (new terminal)
   streamlit run app/streamlit_app.py
   ```

### Access Points

| Service | URL |
|---------|-----|
| API Documentation | http://localhost:8000/docs |
| Streamlit Dashboard | http://localhost:8501 |
| Health Check | http://localhost:8000/health |

## Project Structure

```
Content Analytics/
├── src/
│   ├── api/                 # API clients (YouTube, Instagram)
│   ├── database/            # SQLAlchemy models and queries
│   ├── etl/                 # Data collection pipeline
│   ├── analytics/           # Metrics and trend analysis
│   └── ml/                  # ML models (viral, forecast, sentiment)
├── server/
│   ├── main.py              # FastAPI application
│   └── routes/              # API endpoints
├── app/
│   └── streamlit_app.py     # Dashboard UI
├── tests/                   # Test suite
├── docker-compose.yml       # Docker services
├── Dockerfile               # Multi-stage build
├── requirements.txt         # Python dependencies
└── .env.example             # Environment template
```

## API Endpoints

### YouTube
- `GET /api/youtube/channels` - List tracked channels
- `GET /api/youtube/channels/{id}` - Get channel details
- `GET /api/youtube/channels/{id}/videos` - Get channel videos
- `GET /api/youtube/channels/{id}/growth` - Get growth history
- `POST /api/youtube/channels/collect` - Trigger data collection

### Instagram
- `GET /api/instagram/accounts` - List tracked accounts
- `GET /api/instagram/accounts/{id}/posts` - Get account posts
- `GET /api/instagram/accounts/{id}/growth` - Get growth history

### Analytics
- `GET /api/analytics/youtube/{id}/metrics` - Channel metrics
- `GET /api/analytics/youtube/{id}/trends` - Trend analysis
- `GET /api/analytics/compare` - Compare channels

### ML
- `POST /api/ml/predict/viral` - Predict viral potential
- `GET /api/ml/forecast/subscribers/{id}` - Forecast subscribers
- `GET /api/ml/sentiment/{video_id}` - Analyze comment sentiment

## Environment Variables

```env
# API Keys
YOUTUBE_API_KEY=your_youtube_api_key
INSTAGRAM_ACCESS_TOKEN=your_instagram_token

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/analytics
REDIS_URL=redis://localhost:6379/0

# Server
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
```

## Development

```bash
# Run tests
pytest tests/ -v

# Format code
black .
isort .

# Type checking
mypy src/
```

## License

MIT License - See LICENSE file for details.
