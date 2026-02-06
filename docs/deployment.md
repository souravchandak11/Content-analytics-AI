# Backend Deployment Guide

This guide explains how to deploy the Content Analytics backend and dashboard.

## 🚀 Option 1: Render (Recommended)

The project includes a `render.yaml` configuration file for 1-click deployment on Render.

### Steps:
1.  **Sign up/Login** to [Render](https://render.com).
2.  Click **"New"** > **"Blueprint"**.
3.  Connect your GitHub account and select this repository.
4.  Render will detect the `render.yaml` file and propose the following services:
    *   **content-analytics-api**: The FastAPI backend.
    *   **content-analytics-streamlit**: The Dashboard.
    *   **content-analytics-db**: A managed PostgreSQL database.
    *   **content-analytics-redis**: A Redis cache instance.
5.  **Environment Variables**: You will be prompted to enter values for:
    *   `YOUTUBE_API_KEY`: Your YouTube Data API key.
    *   `INSTAGRAM_ACCESS_TOKEN`: The Instagram Graph API token.
    *   *Note: Database and Redis URLs are automatically injected by the Blueprint.*

6.  Click **"Apply"**. Render will build and deploy the services.

### Verification:
*   Once deployed, the API will be available at `https://content-analytics-api.onrender.com`.
*   The Dashboard will be available at `https://content-analytics-streamlit.onrender.com`.

---

## 🐳 Option 2: Docker (Self-Hosted)

If you have your own VPS (DigitalOcean, AWS EC2, etc.), you can use Docker Compose.

### Steps:
1.  **Clone the repository** to your server.
2.  **Create a `.env` file** based on `.env.example`:
    ```bash
    cp .env.example .env
    # Edit .env and fill in your API keys!
    ```
3.  **Run with Docker Compose**:
    ```bash
    docker-compose up -d --build
    ```
4.  **Access the services**:
    *   Dashboard: `http://your-server-ip:8501`
    *   API Docs: `http://your-server-ip:8000/docs`

---

## ☁️ Option 3: Heroku

1.  **Install Heroku CLI** and login.
2.  **Create App**:
    ```bash
    heroku create content-analytics-app
    ```
3.  **Add Database**:
    ```bash
    heroku addons:create heroku-postgresql:hobby-dev
    ```
4.  **Set Config Vars**:
    ```bash
    heroku config:set YOUTUBE_API_KEY=your_key
    ```
5.  **Deploy**:
    ```bash
    git push heroku main
    ```
