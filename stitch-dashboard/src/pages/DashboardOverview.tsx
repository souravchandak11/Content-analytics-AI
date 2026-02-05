import React from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import MetricCard from '../components/ui/MetricCard';
import { GrowthChart, EngagementBarChart, SentimentPieChart } from '../components/ui/Charts';
import { analyticsApi } from '../lib/api';
import { PlayCircle, Camera, Loader2, TrendingUp, TrendingDown, Star, Youtube, Instagram, Activity, BarChart3, PieChart } from 'lucide-react';

const DashboardOverview = () => {
    const { data: overview, isLoading, error } = useQuery<any>({
        queryKey: ['overview'],
        queryFn: analyticsApi.getOverview,
        refetchInterval: 30000, // Refresh every 30 seconds
    });

    if (isLoading) {
        return (
            <div className="min-h-[60vh] flex items-center justify-center">
                <Loader2 className="w-12 h-12 text-primary animate-spin" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-[60vh] flex flex-col items-center justify-center text-center p-8">
                <h2 className="serif-display text-4xl mb-4 italic">Connection Interrupt</h2>
                <p className="text-charcoal/60 mb-8 max-w-md">Our backend intelligence units are currently out of reach. Please ensure the API is operational.</p>
                <button
                    onClick={() => window.location.reload()}
                    className="px-8 py-3 bg-charcoal text-white text-[10px] font-black uppercase tracking-widest hover:bg-primary transition-colors"
                >
                    Reconnect
                </button>
            </div>
        );
    }

    const creatorInfo = overview?.creator_info;
    const performance = overview?.performance;

    const metrics = [
        {
            label: "Total Audience",
            value: ((overview?.metrics?.total_audience || 0) / 1000000).toFixed(1) + "M",
            delta: `${overview?.growth_forecast || 0}% Growth`,
            deltaType: "positive" as const,
            description: "Aggregated expansion across core demographics in your digital ecosystem."
        },
        {
            label: "Total Reach",
            value: ((overview?.metrics?.total_reach || 0) / 1000000).toFixed(1) + "M",
            delta: "Views",
            deltaType: "positive" as const,
            description: "Real-time visibility metrics identifying the total volume of your creative echo."
        },
        {
            label: "Avg Engagement",
            value: (overview?.metrics?.engagement_avg || 0).toFixed(2) + "%",
            delta: (overview?.metrics?.engagement_avg || 0) > 3 ? "Above Avg" : "Below Avg",
            deltaType: (overview?.metrics?.engagement_avg || 0) > 3 ? "positive" as const : "neutral" as const,
            description: "Quality of interaction normalized across all active content platforms."
        },
        {
            label: "Asset Value",
            value: "$" + ((overview?.metrics?.asset_value_est || 0) / 1000).toFixed(1) + "K",
            delta: "Est. Value",
            deltaType: "trend" as const,
            description: "Estimated brand capital based on current algorithmic velocity and sentiment."
        }
    ];

    const articles = (overview?.feed || []).map((item: any) => ({
        type: item.type === 'YouTube' ? 'YouTube Performance' : 'Instagram Narrative',
        time: new Date(item.timestamp).toLocaleDateString(),
        title: item.title,
        description: item.description,
        stats: {
            [item.type === 'YouTube' ? 'Views' : 'Likes']: item.views > 1000 ? (item.views / 1000).toFixed(1) + 'K' : item.views,
            'Engagement': (item.engagement * 100).toFixed(1) + '%'
        },
        icon: item.type === 'YouTube' ? <PlayCircle size={20} /> : <Camera size={20} />,
        image: item.thumbnail_url
    }));

    return (
        <div className="animate-fade-in">
            {/* Header with Creator Profile */}
            <header className="mb-24 border-b-2 border-charcoal pb-12">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-end">
                    <div className="lg:col-span-8">
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="mb-4 flex items-center gap-4"
                        >
                            <span className="h-px w-12 bg-secondary"></span>
                            <span className="text-xs uppercase tracking-[0.3em] text-secondary font-bold">Command Center Report</span>
                        </motion.div>
                        <motion.h1
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="serif-display text-7xl lg:text-[110px] font-black leading-[0.9] tracking-tighter"
                        >
                            Executive<br /><span className="italic text-primary">Overview</span>
                        </motion.h1>
                    </div>

                    {/* Creator Profile Card */}
                    <div className="lg:col-span-4">
                        {creatorInfo && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: 0.3 }}
                                className="bg-white border border-charcoal p-6 paper-shadow"
                            >
                                <div className="flex items-center gap-4 mb-4">
                                    <div className="relative">
                                        <img
                                            src={creatorInfo.image}
                                            alt={creatorInfo.name}
                                            className="w-16 h-16 rounded-full object-cover border-2 border-charcoal"
                                        />
                                        <div className="absolute -bottom-1 -right-1 bg-charcoal rounded-full p-1">
                                            {creatorInfo.platform === 'YouTube' ?
                                                <Youtube size={12} className="text-white" /> :
                                                <Instagram size={12} className="text-white" />
                                            }
                                        </div>
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="serif-display text-xl font-bold leading-tight">{creatorInfo.name}</h3>
                                        <p className="text-[10px] uppercase tracking-widest text-secondary font-bold">{creatorInfo.platform} Creator</p>
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-charcoal/10">
                                    <div>
                                        <p className="text-[9px] uppercase tracking-widest text-muted-gray mb-1">
                                            {creatorInfo.platform === 'YouTube' ? 'Subscribers' : 'Followers'}
                                        </p>
                                        <p className="serif-display text-2xl font-black">
                                            {((creatorInfo.subscribers || creatorInfo.followers || 0) / 1000000).toFixed(2)}M
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-[9px] uppercase tracking-widest text-muted-gray mb-1">
                                            {creatorInfo.platform === 'YouTube' ? 'Total Views' : 'Posts'}
                                        </p>
                                        <p className="serif-display text-2xl font-black">
                                            {creatorInfo.platform === 'YouTube'
                                                ? ((creatorInfo.total_views || 0) / 1000000000).toFixed(2) + 'B'
                                                : (creatorInfo.posts || 0).toLocaleString()
                                            }
                                        </p>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                        {!creatorInfo && (
                            <div className="flex flex-col lg:items-end gap-2 text-xs uppercase tracking-[0.2em] font-bold">
                                <p>No Creator Data</p>
                                <p className="text-[9px] text-muted-gray italic uppercase">Add channels to get started</p>
                            </div>
                        )}
                    </div>
                </div>
            </header>

            {/* Metrics Grid */}
            <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-32">
                {metrics.map((m, i) => (
                    <MetricCard key={m.label} {...m} index={i} />
                ))}
            </section>

            {/* Performance Insights Section */}
            {performance && performance.top_performers && performance.top_performers.length > 0 && (
                <section className="mb-32">
                    <div className="flex items-baseline justify-between mb-12 border-b border-charcoal pb-6">
                        <div>
                            <span className="text-[10px] uppercase tracking-[0.4em] font-bold text-secondary block mb-2">Analytics</span>
                            <h3 className="serif-display text-5xl font-black">Performance Insights</h3>
                        </div>
                        <p className="text-xs font-bold uppercase tracking-[0.3em]">{performance.total_videos_analyzed} Videos Analyzed</p>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                        {/* Top Performers */}
                        <div className="bg-white border border-charcoal p-8 paper-shadow">
                            <div className="flex items-center gap-3 mb-6">
                                <TrendingUp className="text-primary" size={24} />
                                <h4 className="text-[11px] font-black uppercase tracking-[0.3em]">Top Performing Content</h4>
                            </div>
                            <div className="space-y-4">
                                {performance.top_performers.map((video: any, i: number) => (
                                    <motion.div
                                        key={video.video_id}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.1 * i }}
                                        className="flex items-center gap-4 p-3 bg-offwhite border border-charcoal/10 hover:border-primary transition-colors group"
                                    >
                                        <div className="flex items-center justify-center w-8 h-8 bg-primary text-white font-black serif-display">
                                            {i + 1}
                                        </div>
                                        {video.thumbnail_url && (
                                            <img
                                                src={video.thumbnail_url}
                                                alt={video.title}
                                                className="w-16 h-10 object-cover transition-all"
                                            />
                                        )}
                                        <div className="flex-1 min-w-0">
                                            <p className="serif-text font-medium truncate">{video.title}</p>
                                            <div className="flex gap-4 text-[9px] uppercase tracking-widest text-muted-gray font-bold">
                                                <span>{(video.views / 1000).toFixed(1)}K views</span>
                                                <span className="text-primary">{video.engagement_rate}% eng</span>
                                            </div>
                                        </div>
                                        <Star className="text-secondary" size={16} fill="currentColor" />
                                    </motion.div>
                                ))}
                            </div>
                        </div>

                        {/* Bottom Performers */}
                        {performance.bottom_performers && performance.bottom_performers.length > 0 && (
                            <div className="bg-white border border-charcoal p-8 paper-shadow">
                                <div className="flex items-center gap-3 mb-6">
                                    <TrendingDown className="text-secondary" size={24} />
                                    <h4 className="text-[11px] font-black uppercase tracking-[0.3em]">Needs Improvement</h4>
                                </div>
                                <div className="space-y-4">
                                    {performance.bottom_performers.map((video: any, i: number) => (
                                        <motion.div
                                            key={video.video_id}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: 0.1 * i }}
                                            className="flex items-center gap-4 p-3 bg-offwhite border border-charcoal/10 hover:border-secondary transition-colors group"
                                        >
                                            <div className="flex items-center justify-center w-8 h-8 bg-charcoal/20 text-charcoal font-black serif-display">
                                                {i + 1}
                                            </div>
                                            {video.thumbnail_url && (
                                                <img
                                                    src={video.thumbnail_url}
                                                    alt={video.title}
                                                    className="w-16 h-10 object-cover transition-all"
                                                />
                                            )}
                                            <div className="flex-1 min-w-0">
                                                <p className="serif-text font-medium truncate">{video.title}</p>
                                                <div className="flex gap-4 text-[9px] uppercase tracking-widest text-muted-gray font-bold">
                                                    <span>{(video.views / 1000).toFixed(1)}K views</span>
                                                    <span className="text-secondary">{video.engagement_rate}% eng</span>
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                                <p className="mt-6 text-xs text-charcoal/60 italic border-t border-charcoal/10 pt-4">
                                    Consider analyzing these videos for optimization opportunities.
                                </p>
                            </div>
                        )}
                    </div>
                </section>
            )}

            {/* Interactive Charts Section */}
            <section className="mb-32">
                <div className="flex items-baseline justify-between mb-12 border-b border-charcoal pb-6">
                    <div>
                        <span className="text-[10px] uppercase tracking-[0.4em] font-bold text-primary block mb-2">Analytics</span>
                        <h3 className="serif-display text-5xl font-black">Growth & Engagement</h3>
                    </div>
                    <div className="flex items-center gap-2">
                        <Activity className="text-primary" size={20} />
                        <span className="text-xs font-bold uppercase tracking-[0.2em]">Live Data</span>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                    {/* Subscriber Growth Chart */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-white border border-charcoal p-8 paper-shadow"
                    >
                        <div className="flex items-center gap-3 mb-6">
                            <BarChart3 className="text-primary" size={24} />
                            <div>
                                <h4 className="text-[11px] font-black uppercase tracking-[0.3em]">Subscriber Growth</h4>
                                <p className="text-[9px] text-muted-gray italic">Last 6 weeks performance</p>
                            </div>
                        </div>
                        <div className="h-[300px]">
                            <GrowthChart
                                data={overview?.charts?.growth?.labels?.map((label: string, i: number) => ({
                                    name: label,
                                    value: overview?.charts?.growth?.data?.[i] || 0
                                })) || []}
                            />
                        </div>
                    </motion.div>

                    {/* Top Videos Engagement Chart */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="bg-white border border-charcoal p-8 paper-shadow"
                    >
                        <div className="flex items-center gap-3 mb-6">
                            <TrendingUp className="text-secondary" size={24} />
                            <div>
                                <h4 className="text-[11px] font-black uppercase tracking-[0.3em]">Top Videos Engagement</h4>
                                <p className="text-[9px] text-muted-gray italic">Engagement rate comparison</p>
                            </div>
                        </div>
                        <div className="h-[300px]">
                            <EngagementBarChart
                                data={(performance?.top_performers || []).map((v: any) => ({
                                    name: v.title?.substring(0, 15) + '...' || 'Video',
                                    engagement: v.engagement_rate || 0,
                                    views: v.views || 0
                                }))}
                            />
                        </div>
                    </motion.div>
                </div>

                {/* Sentiment Analysis */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 mt-12">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.3 }}
                        className="bg-white border border-charcoal p-8 paper-shadow"
                    >
                        <div className="flex items-center gap-3 mb-6">
                            <PieChart className="text-primary" size={24} />
                            <div>
                                <h4 className="text-[11px] font-black uppercase tracking-[0.3em]">Audience Sentiment</h4>
                                <p className="text-[9px] text-muted-gray italic">Comment analysis</p>
                            </div>
                        </div>
                        <div className="h-[200px]">
                            <SentimentPieChart
                                data={[
                                    { name: 'Positive', value: overview?.charts?.sentiment?.distribution?.positive || 60, color: '#2d6a6d' },
                                    { name: 'Neutral', value: overview?.charts?.sentiment?.distribution?.neutral || 25, color: '#d4d4d4' },
                                    { name: 'Negative', value: overview?.charts?.sentiment?.distribution?.negative || 15, color: '#c06c52' }
                                ]}
                            />
                        </div>
                    </motion.div>

                    {/* Quick Stats Cards */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.4 }}
                        className="bg-charcoal text-white p-8 paper-shadow"
                    >
                        <h4 className="text-[11px] font-black uppercase tracking-[0.3em] mb-6 text-white/70">Real-Time Metrics</h4>
                        <div className="space-y-6">
                            <div>
                                <p className="text-[9px] uppercase tracking-widest text-white/50 mb-1">Growth Forecast</p>
                                <p className="serif-display text-4xl font-black text-primary">+{overview?.growth_forecast || 0}%</p>
                            </div>
                            <div>
                                <p className="text-[9px] uppercase tracking-widest text-white/50 mb-1">Sentiment Score</p>
                                <p className="serif-display text-4xl font-black">{overview?.charts?.sentiment?.score || 0}/100</p>
                            </div>
                            <div>
                                <p className="text-[9px] uppercase tracking-widest text-white/50 mb-1">Retention Index</p>
                                <p className="serif-display text-4xl font-black text-secondary">{overview?.retention_index || 0}%</p>
                            </div>
                        </div>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.5 }}
                        className="bg-gradient-to-br from-primary to-primary/80 text-white p-8 paper-shadow"
                    >
                        <h4 className="text-[11px] font-black uppercase tracking-[0.3em] mb-6 text-white/80">Competitor Analysis</h4>
                        <div className="space-y-4">
                            {['Engagement', 'Growth', 'Content', 'Reach', 'Authority'].map((metric, i) => (
                                <div key={metric} className="flex items-center gap-3">
                                    <span className="text-[9px] uppercase tracking-widest w-20">{metric}</span>
                                    <div className="flex-1 h-2 bg-white/20 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${overview?.charts?.competitor?.you?.[i] || 70}%` }}
                                            transition={{ duration: 1, delay: 0.5 + i * 0.1 }}
                                            className="h-full bg-white rounded-full"
                                        />
                                    </div>
                                    <span className="text-sm font-black">{overview?.charts?.competitor?.you?.[i] || 70}</span>
                                </div>
                            ))}
                        </div>
                        <p className="mt-4 text-[9px] text-white/60 italic border-t border-white/20 pt-4">You outperform 78% of creators in your niche</p>
                    </motion.div>
                </div>
            </section>

            {/* Editorial Feed */}
            <section>
                <div className="flex flex-col md:flex-row md:items-baseline justify-between mb-16 border-b border-charcoal pb-6">
                    <h3 className="serif-display text-5xl font-black italic">Recent Editorial Feed</h3>
                    <p className="text-xs font-bold uppercase tracking-[0.3em] mt-4 md:mt-0">The Latest Creative Dispatches</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-12 gap-y-20">
                    {articles.map((art: any, i: number) => (
                        <motion.article
                            key={art.title + i}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.2 * i }}
                            className="flex flex-col group"
                        >
                            <div className="relative overflow-hidden mb-8 aspect-[3/4] border border-charcoal/10">
                                <img src={art.image} alt={art.title} className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110" />
                                <div className="absolute top-6 right-6 p-3 bg-charcoal text-white rounded-full">
                                    {art.icon}
                                </div>
                            </div>
                            <div className="flex items-center gap-4 mb-4">
                                <span className="text-[9px] font-black uppercase tracking-[0.4em] text-secondary">{art.type}</span>
                                <span className="h-px flex-grow bg-charcoal/10"></span>
                                <span className="text-[9px] font-medium text-muted-gray italic">{art.time}</span>
                            </div>
                            <h4 className="serif-display text-3xl font-bold leading-tight mb-4 group-hover:text-primary transition-colors cursor-pointer">{art.title}</h4>
                            <p className="serif-text text-lg text-charcoal/70 mb-8 line-clamp-3 leading-relaxed">{art.description}</p>
                            <div className="mt-auto pt-6 border-t border-charcoal/10 grid grid-cols-2">
                                {Object.entries(art.stats).map(([k, v]) => (
                                    <div key={k}>
                                        <span className="text-[9px] uppercase tracking-widest text-muted-gray block mb-1">{k}</span>
                                        <span className="text-xl font-black serif-display">{v as React.ReactNode}</span>
                                    </div>
                                ))}
                            </div>
                        </motion.article>
                    ))}
                </div>
            </section>
        </div>
    );
};

export default DashboardOverview;
