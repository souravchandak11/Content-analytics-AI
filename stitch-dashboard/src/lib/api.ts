import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface Channel {
    channel_id: string;
    title: string;
    thumbnail_url?: string;
    subscribers?: number;
    total_views?: number;
    stats?: {
        total_views: number;
        avg_engagement: number;
    };
    health_score?: {
        total_score: number;
        grade: string;
    } | number;
}

export interface Video {
    video_id: string;
    title: string;
    description?: string;
    thumbnail_url?: string;
    views: number;
    likes: number;
    engagement_rate?: number;
    published_at?: string;
}

export interface Comment {
    text: string;
    author?: string;
    label?: string;
}

export interface SentimentData {
    total_comments: number;
    sentiment_distribution: {
        positive: number;
        neutral: number;
        negative: number;
    };
    positive_ratio?: number;
    neutral_ratio?: number;
    negative_ratio?: number;
    top_comments?: Comment[];
    positive_examples?: Comment[];
}

export const analyticsApi = {
    getOverview: () => api.get('/ai/dashboard/summary').then(res => res.data),
    listYoutubeChannels: () => api.get<Channel[]>('/youtube/channels').then(res => res.data),
    getYoutubeMetrics: (channelId: string) => api.get<Channel>(`/analytics/youtube/${channelId}/metrics`).then(res => res.data),
    getYoutubeVideos: (channelId: string) => api.get<Video[]>(`/youtube/channels/${channelId}/videos`).then(res => res.data),
    getYoutubeTrends: (channelId: string) => api.get(`/analytics/youtube/${channelId}/trends`).then(res => res.data),
    listInstagramAccounts: () => api.get('/instagram/accounts').then(res => res.data),
    getInstagramMetrics: (instagramId: string) => api.get(`/analytics/instagram/${instagramId}/metrics`).then(res => res.data),
    getInstagramPosts: (instagramId: string) => api.get(`/instagram/accounts/${instagramId}/posts`).then(res => res.data),
    getForecasting: (platform: string, id: string) => api.get(`/ml/forecast?platform=${platform}&id=${id}`).then(res => res.data),
    forecastSubscribers: (channelId: string) => api.get(`/ml/forecast/subscribers/${channelId}`).then(res => res.data),
    forecastViews: (channelId: string) => api.get(`/ml/forecast/views/${channelId}`).then(res => res.data),
    getVideoSentiment: (videoId: string) => api.get<SentimentData>(`/ml/sentiment/${videoId}`).then(res => res.data),
};

export default api;
