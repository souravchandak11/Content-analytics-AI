"""Streamlit Dashboard for Content Analytics Tool."""

import os
import sys
import io
from datetime import datetime

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy.orm import Session

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.sync_service import SyncService
from src.database import get_db, init_db
from src.database.queries import YouTubeQueries, InstagramQueries
from src.analytics.metrics import EngagementMetrics, SentimentAnalyzer
from src.ml.prediction import GrowthPredictor

# Page configuration
st.set_page_config(
    page_title="Content Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode (re-using previous styles with enhancements)
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%); }
    [data-testid="stSidebar"] { background: rgba(26, 26, 46, 0.95); border-right: 1px solid rgba(255, 255, 255, 0.1); }
    .metric-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 24px; margin: 12px 0; backdrop-filter: blur(10px); }
    .metric-value { font-size: 2rem; font-weight: 700; color: #00d4ff; }
    .metric-label { font-size: 0.9rem; color: rgba(255, 255, 255, 0.7); text-transform: uppercase; }
    h1, h2, h3 { color: #fff !important; }
    .stButton>button { background: linear-gradient(90deg, #667eea, #764ba2); color: white; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)


def format_number(num: int) -> str:
    if num >= 1_000_000: return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000: return f"{num / 1_000:.1f}K"
    return str(num)


def render_metric_card(label: str, value: str, delta: str = None, delta_positive: bool = True):
    delta_html = f'<div style="color: {"#00ff88" if delta_positive else "#ff4757"} font-size: 0.8rem;">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def get_real_data(db: Session, yt_id: str, ig_id: str):
    yt_q = YouTubeQueries(db)
    ig_q = InstagramQueries(db)
    
    # YouTube Data
    channels = yt_q.get_all_channels()
    yt_channel = next((c for c in channels if c.channel_id == yt_id), None) if yt_id else (channels[0] if channels else None)
    
    yt_data = None
    if yt_channel:
        snapshots = yt_q.get_channel_history(yt_channel.channel_id)
        # Convert objects to dicts for UI use
        yt_data = {
            'channel': {
                'title': yt_channel.title,
                'subscriber_count': snapshots[0].subscriber_count if snapshots else 0,
                'view_count': snapshots[0].view_count if snapshots else 0,
                'video_count': snapshots[0].video_count if snapshots else 0
            },
            'snapshots': [{'snapshot_date': s.snapshot_date, 'subscriber_count': s.subscriber_count} for s in snapshots],
            'videos': [{'title': v.title, 'view_count': v.view_count, 'like_count': v.like_count, 'comment_count': v.comment_count} for v in yt_q.get_top_videos(yt_channel.channel_id)],
            'comments': [] # Would fetch if needed
        }
    
    # Instagram Data
    accounts = ig_q.get_all_accounts()
    ig_account = next((a for a in accounts if a.account_id == ig_id), None) if ig_id else (accounts[0] if accounts else None)
    
    ig_data = None
    if ig_account:
        snapshots = ig_q.get_account_history(ig_account.account_id)
        ig_data = {
            'account': {
                'username': ig_account.username,
                'followers_count': snapshots[0].followers_count if snapshots else 0,
                'media_count': snapshots[0].media_count if snapshots else 0
            },
            'snapshots': [{'snapshot_date': s.snapshot_date, 'followers_count': s.followers_count} for s in snapshots],
            'posts': [{'caption': p.caption, 'like_count': p.like_count, 'comments_count': p.comments_count, 'thumbnail_url': p.thumbnail_url} for p in ig_q.get_recent_posts(ig_account.account_id)]
        }
        
    return yt_data, ig_data


def render_forecast_chart(snapshots: list, value_field: str, label: str):
    if len(snapshots) < 5:
        st.info(f"Not enough data for {label} forecasting (need at least 5 snapshots)")
        return
        
    predictor = GrowthPredictor()
    forecast = predictor.forecast(snapshots, periods=30, value_field=value_field)
    
    if forecast:
        hist_df = pd.DataFrame(forecast['historical'])
        fore_df = pd.DataFrame(forecast['forecast'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist_df['ds'], y=hist_df['y'], name='Historical', line=dict(color='#00d4ff')))
        fig.add_trace(go.Scatter(x=fore_df['ds'], y=fore_df['yhat'], name='Forecast', line=dict(color='#7b2ff7', dash='dash')))
        fig.add_trace(go.Scatter(x=fore_df['ds'], y=fore_df['yhat_upper'], fill=None, mode='lines', line_color='rgba(0,0,0,0)', showlegend=False))
        fig.add_trace(go.Scatter(x=fore_df['ds'], y=fore_df['yhat_lower'], fill='tonexty', mode='lines', line_color='rgba(0,0,0,0)', name='Confidence Interval', fillcolor='rgba(123, 47, 247, 0.1)'))
        
        fig.update_layout(template='plotly_dark', margin=dict(l=20, r=20, t=20, b=20), height=300)
        st.plotly_chart(fig, use_container_width=True)


def main():
    db = next(get_db())
    yt_id = st.sidebar.text_input("YouTube Channel ID")
    ig_id = st.sidebar.text_input("Instagram Account ID")
    
    if st.sidebar.button("🔄 Sync with API"):
        with st.spinner("Fetching latest data..."):
            sync = SyncService(db)
            results = sync.sync_all(yt_channel_id=yt_id if yt_id else None)
            if results["youtube"]: st.sidebar.success("YouTube synced!")
            if results["instagram"]: st.sidebar.success("Instagram synced!")

    yt_data, ig_data = get_real_data(db, yt_id, ig_id)
    
    # Navigation
    page = st.sidebar.radio("Navigate", ["📊 Overview", "📺 YouTube", "📸 Instagram"])
    
    if page == "📊 Overview":
        st.header("Unified Content Analytics")
        if not yt_data and not ig_data:
            st.warning("No data found in database. Please enter IDs and click 'Sync with API'.")
            return
            
        cols = st.columns(4)
        if yt_data:
            with cols[0]: render_metric_card("YT Subscribers", format_number(yt_data['channel']['subscriber_count']))
            with cols[1]: render_metric_card("YT Views", format_number(yt_data['channel']['view_count']))
        if ig_data:
            with cols[2]: render_metric_card("IG Followers", format_number(ig_data['account']['followers_count']))
            
    elif page == "📺 YouTube" and yt_data:
        st.header(f"YouTube: {yt_data['channel']['title']}")
        st.subheader("Subscriber Forecast (30 Days)")
        render_forecast_chart(yt_data['snapshots'], 'subscriber_count', "Subscribers")
        
        st.subheader("Top Performing Videos")
        st.table(pd.DataFrame(yt_data['videos']))
        
    elif page == "📸 Instagram" and ig_data:
        st.header(f"Instagram: {ig_data['account']['username']}")
        st.subheader("Follower Forecast (30 Days)")
        render_forecast_chart(ig_data['snapshots'], 'followers_count', "Followers")
        
        st.subheader("Recent Gallery")
        cols = st.columns(4)
        for i, post in enumerate(ig_data['posts'][:8]):
            with cols[i%4]: st.image(post['thumbnail_url'], caption=post['caption'][:50] if post['caption'] else "")

    # Export Section
    if (yt_data or ig_data) and st.sidebar.button("📥 Export Report (CSV)"):
        output = io.StringIO()
        if yt_data: pd.DataFrame(yt_data['videos']).to_csv(output, index=False)
        st.download_button("Download CSV", output.getvalue(), "analytics_report.csv", "text/csv")


if __name__ == "__main__":
    main()
