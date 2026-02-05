"""
Content Analytics Platform - Streamlit Dashboard
================================================
Main dashboard application with multi-page navigation.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from streamlit_option_menu import option_menu
import requests
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(
    page_title="Content Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, #FF0000, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        margin: 0.5rem 0;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = os.getenv('API_URL', 'http://localhost:8000')


def check_api_connection():
    """Check if API is available."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Main dashboard application."""
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=Analytics", width=150)
        st.markdown("---")
        
        selected = option_menu(
            menu_title="Navigation",
            options=[
                "Dashboard",
                "YouTube Analytics",
                "Instagram Analytics",
                "ML Predictions",
                "AI Insights",
                "Data Collection",
                "Settings"
            ],
            icons=[
                "house",
                "youtube",
                "instagram",
                "robot",
                "cpu",
                "cloud-download",
                "gear"
            ],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5px"},
                "icon": {"color": "#FF6B6B", "font-size": "18px"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "5px",
                    "--hover-color": "#f0f2f6"
                },
                "nav-link-selected": {"background-color": "#667eea"},
            }
        )
        
        st.markdown("---")
        
        # API Status
        api_status = check_api_connection()
        if api_status:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
    
    # Main content
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "YouTube Analytics":
        show_youtube_analytics()
    elif selected == "Instagram Analytics":
        show_instagram_analytics()
    elif selected == "ML Predictions":
        show_ml_predictions()
    elif selected == "AI Insights":
        show_ai_insights()
    elif selected == "Data Collection":
        show_data_collection()
    elif selected == "Settings":
        show_settings()


def show_dashboard():
    """Main dashboard overview."""
    st.markdown('<h1 class="main-header">📊 Content Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Fetch Summary Data
    try:
        response = requests.get(f"{API_URL}/api/ai/dashboard/summary")
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('metrics', {})
        else:
            metrics = {}
    except:
        metrics = {}

    # Quick stats row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Audience",
            value=f"{metrics.get('total_audience', 0):,}",
            delta=f"{data.get('growth_forecast', 0)}% Growth" if metrics else None
        )
    
    with col2:
        st.metric(
            label="Total Reach",
            value=f"{metrics.get('total_reach', 0):,}",
            delta="Views"
        )
    
    with col3:
        st.metric(
            label="Avg Engagement",
            value=f"{metrics.get('engagement_avg', 0)}%",
            delta="Above Avg"
        )
    
    with col4:
        st.metric(
            label="Asset Value",
            value=f"${metrics.get('asset_value_est', 0):,}",
            delta="Est."
        )
    
    st.markdown("---")
    
    # Welcome message
    st.markdown("""
    ### Welcome to Content Analytics Platform! 🚀
    
    This platform helps you analyze and optimize your YouTube and Instagram content performance.
    
    **Key Features:**
    - 📈 **Real-time Analytics** - Track views, engagement, and growth
    - 🤖 **ML Predictions** - Predict viral potential and forecast growth
    - 💡 **AI Recommendations** - Get topic ideas and timing suggestions
    - 🏢 **Competitor Analysis** - Benchmarking and gap identification
    - 📍 **Topic Clustering** - Visualizing content themes
    - 💬 **Sentiment Analysis** - Understand audience feedback
    
    **Getting Started:**
    1. Go to **Data Collection** to add your first YouTube channel or Instagram account
    2. View analytics in **YouTube Analytics** or **Instagram Analytics**
    3. Get predictions in **ML Predictions**
    """)
    
    # Quick actions
    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add YouTube Channel", use_container_width=True):
            st.session_state['page'] = 'data_collection'
            st.rerun()
    
    with col2:
        if st.button("➕ Add Instagram Account", use_container_width=True):
            st.session_state['page'] = 'data_collection'
            st.rerun()
    
    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()


def show_youtube_analytics():
    """YouTube analytics page."""
    st.markdown("## 📺 YouTube Analytics")
    
    # Channel selector
    channel_id = st.text_input("Enter YouTube Channel ID", placeholder="UC...")
    
    if channel_id:
        try:
            # Fetch channel data
            response = requests.get(f"{API_URL}/api/youtube/channels/{channel_id}")
            
            if response.status_code == 200:
                channel = response.json()
                
                st.success(f"Channel: **{channel.get('title', 'Unknown')}**")
                
                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Subscribers", f"{channel.get('subscribers', 0):,}")
                with col2:
                    st.metric("Total Views", f"{channel.get('total_views', 0):,}")
                with col3:
                    st.metric("Videos", f"{channel.get('total_videos', 0):,}")
                
                st.markdown("---")
                
                # Tabs for different views
                tab1, tab2, tab3 = st.tabs(["📹 Videos", "📈 Growth", "🎯 Top Performers"])
                
                with tab1:
                    videos_resp = requests.get(f"{API_URL}/api/youtube/channels/{channel_id}/videos?limit=20")
                    if videos_resp.status_code == 200:
                        videos = videos_resp.json()
                        for video in videos:
                            with st.expander(f"📹 {video['title'][:60]}..."):
                                st.write(f"Views: {video['views']:,}")
                                st.write(f"Likes: {video['likes']:,}")
                                st.write(f"Engagement: {video.get('engagement_rate', 0):.2%}")
                
                with tab2:
                    growth_resp = requests.get(f"{API_URL}/api/youtube/channels/{channel_id}/growth?days=30")
                    if growth_resp.status_code == 200:
                        growth = growth_resp.json()
                        st.line_chart({
                            s['date']: s['subscribers']
                            for s in growth.get('snapshots', [])
                        })
                
                with tab3:
                    top_resp = requests.get(f"{API_URL}/api/youtube/channels/{channel_id}/top-videos?limit=5")
                    if top_resp.status_code == 200:
                        top_videos = top_resp.json()
                        for i, video in enumerate(top_videos, 1):
                            st.write(f"**#{i}** {video['title'][:50]}... - {video['views']:,} views")
            else:
                st.warning("Channel not found. Try collecting data first.")
                
        except requests.RequestException:
            st.error("Could not connect to API. Please check if the server is running.")
    else:
        st.info("Enter a YouTube channel ID to view analytics")


def show_instagram_analytics():
    """Instagram analytics page."""
    st.markdown("## 📸 Instagram Analytics")
    
    instagram_id = st.text_input("Enter Instagram Account ID", placeholder="Account ID")
    
    if instagram_id:
        try:
            response = requests.get(f"{API_URL}/api/instagram/accounts/{instagram_id}")
            
            if response.status_code == 200:
                account = response.json()
                
                st.success(f"Account: **@{account.get('username', 'Unknown')}**")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Followers", f"{account.get('followers_count', 0):,}")
                with col2:
                    st.metric("Following", f"{account.get('follows_count', 0):,}")
                with col3:
                    st.metric("Posts", f"{account.get('media_count', 0):,}")
            else:
                st.warning("Account not found. Try collecting data first.")
        except:
            st.error("Could not connect to API")
    else:
        st.info("Enter an Instagram account ID to view analytics")


def show_ml_predictions():
    """ML predictions page."""
    st.markdown("## 🤖 ML Predictions")
    
    tab1, tab2, tab3 = st.tabs(["🔮 Viral Prediction", "📈 Forecasting", "💬 Sentiment Analysis"])
    
    with tab1:
        st.markdown("### Predict Viral Potential")
        
        title = st.text_input("Video Title")
        description = st.text_area("Description")
        tags = st.text_input("Tags (comma-separated)")
        duration = st.number_input("Duration (seconds)", min_value=0, value=300)
        subscribers = st.number_input("Channel Subscribers", min_value=0, value=1000)
        
        if st.button("Predict"):
            try:
                response = requests.post(f"{API_URL}/api/ml/predict/viral", json={
                    "title": title,
                    "description": description,
                    "tags": [t.strip() for t in tags.split(",") if t.strip()],
                    "duration_seconds": duration,
                    "channel_subscribers": subscribers
                })
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.markdown("### Results")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Viral Score", f"{result.get('viral_score', 0):.1f}/100")
                    with col2:
                        st.metric("Confidence", result.get('confidence', 'unknown').title())
                    
                    if result.get('is_viral'):
                        st.success("🔥 This content has high viral potential!")
                    else:
                        st.info("This content has moderate viral potential.")
            except:
                st.error("Prediction failed")
    
    with tab2:
        st.markdown("### Growth Forecasting")
        channel_id = st.text_input("Channel ID for Forecast")
        periods = st.slider("Forecast Days", 7, 90, 30)
        
        if st.button("Generate Forecast"):
            try:
                response = requests.get(
                    f"{API_URL}/api/ml/forecast/subscribers/{channel_id}?periods={periods}"
                )
                if response.status_code == 200:
                    forecast = response.json()
                    st.write(forecast.get('summary', {}))
            except:
                st.error("Forecasting failed")
    
    with tab3:
        st.markdown("### Sentiment Analysis")
        texts = st.text_area("Enter comments (one per line)")
        
        if st.button("Analyze Sentiment"):
            lines = [l.strip() for l in texts.split("\n") if l.strip()]
            if lines:
                try:
                    response = requests.post(f"{API_URL}/api/ml/sentiment/analyze", json=lines)
                    if response.status_code == 200:
                        result = response.json()
                        st.metric("Average Sentiment", f"{result.get('avg_sentiment', 0):.2f}")
                        st.write("Distribution:", result.get('distribution', {}))
                except:
                    st.error("Analysis failed")


def show_ai_insights():
    """AI Insights and recommendations page."""
    st.markdown("## 🧠 AI Insights & recommendations")
    
    channel_id = st.text_input("YouTube Channel ID for AI Analysis", placeholder="UC...")
    
    if channel_id:
        tab1, tab2, tab3 = st.tabs(["💡 Recommendations", "🏢 Competitor Benchmarking", "📍 Topic Clusters"])
        
        with tab1:
            if st.button("Generate Recommendations"):
                with st.spinner("Analyzing channel data..."):
                    try:
                        response = requests.get(f"{API_URL}/api/ai/recommendations/{channel_id}")
                        if response.status_code == 200:
                            data = response.json()
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("### 💡 Content Ideas")
                                for idea in data.get('ideas', []):
                                    st.info(f"**{idea['title']}**\n\n*Rationale: {idea['rationale']}*")
                            
                            with col2:
                                st.markdown("### 📈 Winning Topics")
                                for topic in data.get('topics', []):
                                    st.success(f"**{topic['topic'].title()}** (Score: {topic['engagement_score']:.1f})")
                                
                                st.markdown("### ⏰ Best Posting Time")
                                timing = data.get('timing', {})
                                st.write(f"Most active day: **{timing.get('best_day', 'N/A')}**")
                                st.write(f"Optimal hour: **{timing.get('best_hour_utc', 0)}:00 UTC**")
                        else:
                            st.error("Could not fetch recommendations")
                    except:
                        st.error("API Error")
                        
        with tab2:
            st.markdown("### Competitor Benchmarking")
            comp_ids = st.text_input("Enter Competitor Channel IDs (comma-separated)")
            if st.button("Compare with Competitors"):
                if comp_ids:
                    with st.spinner("Analyzing competition..."):
                        ids_list = [i.strip() for i in comp_ids.split(",") if i.strip()]
                        try:
                            response = requests.post(f"{API_URL}/api/ai/competitor/compare", json={
                                "your_channel_id": channel_id,
                                "competitor_channel_ids": ids_list
                            })
                            if response.status_code == 200:
                                result = response.json()
                                comparison = result.get('comparison', {})
                                st.metric("Your Market Rank", f"#{comparison.get('your_rank', 0)}", f"{comparison.get('percentile', 0)}th percentile")
                                
                                # Rankings table
                                st.table(comparison.get('rankings', []))
                                
                                st.markdown("### 🔍 Content Gaps")
                                gaps = result.get('gaps', {}).get('content_gaps', [])
                                if gaps:
                                    for gap in gaps:
                                        st.warning(f"Feature opportunity: **{gap['topic']}** (Opportunity Score: {gap['opportunity_score']})")
                            else:
                                st.error("Comparison failed")
                        except:
                            st.error("API Error")
        
        with tab3:
            st.markdown("### Topic Clustering")
            if st.button("Analyze Content Themes"):
                with st.spinner("Clustering videos..."):
                    try:
                        response = requests.get(f"{API_URL}/api/ai/topics/cluster/{channel_id}")
                        if response.status_code == 200:
                            data = response.json()
                            if 'error' in data:
                                st.error(data['error'])
                            else:
                                clusters = data.get('clusters', [])
                                for c in clusters:
                                    with st.expander(f"📍 {c['name']} ({c['video_count']} videos)"):
                                        st.write(f"Keywords: {', '.join(c['keywords'])}")
                                        st.write(f"Avg Views: {c['avg_views']:,}")
                                        st.write(f"Performance Index: {c['performance_index']}")
                        else:
                            st.error("Clustering failed")
                    except:
                        st.error("API Error")
    else:
        st.info("Please enter a Channel ID to unlock AI Insights.")


def show_data_collection():
    """Data collection page."""
    st.markdown("## 📥 Data Collection")
    
    tab1, tab2 = st.tabs(["YouTube", "Instagram"])
    
    with tab1:
        st.markdown("### Collect YouTube Channel Data")
        
        channel_id = st.text_input("YouTube Channel ID", placeholder="UC...")
        max_videos = st.slider("Max Videos to Collect", 10, 100, 50)
        collect_comments = st.checkbox("Collect Comments", value=True)
        
        if st.button("Start YouTube Collection"):
            with st.spinner("Collecting data..."):
                try:
                    response = requests.post(f"{API_URL}/api/youtube/channels/collect", json={
                        "channel_id": channel_id,
                        "max_videos": max_videos,
                        "collect_comments": collect_comments
                    })
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Collected {result.get('videos_collected', 0)} videos!")
                        st.json(result)
                    else:
                        st.error(f"Collection failed: {response.text}")
                except:
                    st.error("Could not connect to API")
    
    with tab2:
        st.markdown("### Collect Instagram Account Data")
        
        instagram_id = st.text_input("Instagram User ID", value="me")
        max_posts = st.slider("Max Posts to Collect", 10, 50, 25)
        
        if st.button("Start Instagram Collection"):
            with st.spinner("Collecting data..."):
                try:
                    response = requests.post(f"{API_URL}/api/instagram/accounts/collect", json={
                        "user_id": instagram_id,
                        "max_posts": max_posts
                    })
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Collected {result.get('posts_collected', 0)} posts!")
                    else:
                        st.error(f"Collection failed: {response.text}")
                except:
                    st.error("Could not connect to API")


def show_settings():
    """Settings page."""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### API Configuration")
    st.text_input("API URL", value=API_URL, disabled=True)
    
    st.markdown("### Model Status")
    try:
        response = requests.get(f"{API_URL}/api/ml/model/status")
        if response.status_code == 200:
            st.json(response.json())
    except:
        st.warning("Could not fetch model status")
    
    st.markdown("### System Information")
    try:
        response = requests.get(f"{API_URL}/info")
        if response.status_code == 200:
            st.json(response.json())
    except:
        st.warning("Could not fetch system info")


if __name__ == "__main__":
    main()
