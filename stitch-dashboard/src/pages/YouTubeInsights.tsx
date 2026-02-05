import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { TrendingUp, Users, Eye, BarChart2, CheckCircle2, Star, Loader2, Youtube } from 'lucide-react';
import MetricCard from '../components/ui/MetricCard';
import { analyticsApi, Channel, Video } from '@/lib/api';
import { PerformanceChart } from '../components/ui/Charts';

const YouTubeInsights = () => {
    const [selectedChannelId, setSelectedChannelId] = useState<string | null>(null);

    // Fetch all channels to get an ID if not selected
    const { data: channels } = useQuery<Channel[]>({
        queryKey: ['youtube-channels'],
        queryFn: analyticsApi.listYoutubeChannels,
    });

    const channelId = selectedChannelId || channels?.[0]?.channel_id;
    const selectedChannel = channels?.find((c: Channel) => c.channel_id === channelId);

    const { data: youtubeData, isLoading: metricsLoading } = useQuery<Channel>({
        queryKey: ['youtube-metrics', channelId],
        queryFn: () => analyticsApi.getYoutubeMetrics(channelId!),
        enabled: !!channelId,
    });

    const { data: videos, isLoading: videosLoading } = useQuery<Video[]>({
        queryKey: ['youtube-videos', channelId],
        queryFn: () => analyticsApi.getYoutubeVideos(channelId!),
        enabled: !!channelId,
    });

    if (metricsLoading || videosLoading) {
        return (
            <div className="min-h-[60vh] flex items-center justify-center">
                <Loader2 className="w-12 h-12 text-primary animate-spin" />
            </div>
        );
    }

    const metrics = [
        {
            label: "Reach Total",
            value: ((youtubeData?.stats?.total_views || 0) / 1000000).toFixed(1) + "M",
            delta: "5.2% Increase",
            deltaType: "positive" as const,
            description: "Total impressions across the YouTube ecosystem analyzed for the current period."
        },
        {
            label: "Audience Base",
            value: ((youtubeData?.subscribers || 0) / 1000000).toFixed(1) + "M",
            delta: "Stable",
            deltaType: "neutral" as const,
            description: "Core subscriber count reflecting long-term community growth and authority."
        },
        {
            label: "Eng. Coefficient",
            value: ((youtubeData?.stats?.avg_engagement || 0) * 100).toFixed(1) + "%",
            delta: "+0.4%",
            deltaType: "positive" as const,
            description: "Average interaction rate per video, normalized for audience size."
        },
        {
            label: "Health Score",
            value: (typeof youtubeData?.health_score === 'number'
                ? youtubeData.health_score
                : youtubeData?.health_score?.total_score || 0) + "/100",
            delta: typeof youtubeData?.health_score === 'object' ? youtubeData.health_score.grade : "Optimal",
            deltaType: "trend" as const,
            description: "Proprietary metric measuring consistency, growth, and audience sentiment."
        }
    ];

    const videoStats = (videos || []).slice(0, 3).map((v: Video) => ({
        title: v.title,
        plays: (v.views / 1000).toFixed(1) + "K",
        ctr: v.engagement_rate ? (v.engagement_rate * 100).toFixed(1) + "%" : "0.0%",
        time: "Latest",
        type: "Analysis",
        image: v.thumbnail_url || "https://lh3.googleusercontent.com/aida-public/placeholder"
    }));

    const tableData = (videos || []).slice(0, 5).map((v: Video) => ({
        metric: v.title,
        pathway: "Direct Discovery",
        volume: (v.views / 1000).toFixed(1) + "K",
        momentum: v.likes > 1000 ? "High" : "Stable",
        status: v.likes > 2000 ? "viral" : "high"
    }));

    return (
        <div className="animate-fade-in">
            <header className="mb-24">
                <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-12 border-b-2 border-charcoal pb-12">
                    <div className="max-w-4xl">
                        <p className="text-xs uppercase tracking-[0.3em] text-secondary font-bold mb-6 italic">Deep Dive Feature</p>
                        <motion.h2
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="serif-display text-7xl lg:text-[110px] font-bold leading-[0.85] tracking-tight"
                        >
                            YouTube Insights <br /><span className="italic text-primary">Editorial.</span>
                        </motion.h2>
                        <p className="mt-8 text-xl text-zinc-500 font-light max-w-xl leading-relaxed italic border-l-2 border-primary pl-6">
                            An analytical exploration of audience sentiment and cross-platform growth dynamics for the modern creative professional.
                        </p>
                    </div>

                    {/* Channel Profile Card */}
                    <div className="flex flex-col items-end gap-6 min-w-[280px]">
                        {selectedChannel ? (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="bg-white border border-charcoal p-5 paper-shadow w-full"
                            >
                                <div className="flex items-center gap-4 mb-4">
                                    <div className="relative">
                                        <img
                                            src={selectedChannel.thumbnail_url || 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face'}
                                            alt={selectedChannel.title}
                                            className="w-14 h-14 rounded-full object-cover border-2 border-charcoal"
                                        />
                                        <div className="absolute -bottom-1 -right-1 bg-red-600 rounded-full p-1">
                                            <Youtube size={10} className="text-white" />
                                        </div>
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h3 className="serif-display text-lg font-bold leading-tight truncate">{selectedChannel.title}</h3>
                                        <p className="text-[9px] uppercase tracking-widest text-secondary font-bold">YouTube Creator</p>
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-3 pt-3 border-t border-charcoal/10">
                                    <div>
                                        <p className="text-[9px] uppercase tracking-widest text-muted-gray mb-1">Subscribers</p>
                                        <p className="serif-display text-xl font-black">
                                            {((selectedChannel.subscribers || 0) / 1000000).toFixed(2)}M
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-[9px] uppercase tracking-widest text-muted-gray mb-1">Total Views</p>
                                        <p className="serif-display text-xl font-black">
                                            {((selectedChannel.total_views || 0) / 1000000000).toFixed(2)}B
                                        </p>
                                    </div>
                                </div>
                            </motion.div>
                        ) : (
                            <div className="text-right">
                                <p className="text-[10px] uppercase tracking-widest text-muted-gray mb-1">No Channel Selected</p>
                                <p className="serif-display text-lg italic">Add a channel to view analytics</p>
                            </div>
                        )}

                        {/* Channel Selector */}
                        {channels && channels.length > 1 && (
                            <select
                                value={channelId || ''}
                                onChange={(e) => setSelectedChannelId(e.target.value)}
                                className="w-full text-[10px] uppercase tracking-widest font-bold border border-charcoal/20 p-2 bg-white"
                            >
                                {channels.map((ch: Channel) => (
                                    <option key={ch.channel_id} value={ch.channel_id}>
                                        {ch.title}
                                    </option>
                                ))}
                            </select>
                        )}
                    </div>
                </div>
            </header>

            {/* Metrics Grid */}
            <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-0 mb-32 border-b border-border-soft">
                {metrics.map((m, i) => (
                    <div key={m.label} className={`py-12 ${i === 0 ? 'pr-12' : i === 3 ? 'pl-12' : 'px-12'} ${i !== 3 ? 'border-r border-border-soft' : ''}`}>
                        <MetricCard {...m} index={i} />
                    </div>
                ))}
            </section>

            {/* Retention Curve Section */}
            <section className="mb-32">
                <div className="grid lg:grid-cols-12 gap-16">
                    <div className="lg:col-span-5 flex flex-col justify-center">
                        <h3 className="serif-display text-4xl font-bold mb-8 italic">Cross-Platform Growth Dynamics</h3>
                        <div className="serif-text text-lg text-zinc-600 leading-loose">
                            <p className="mb-6 dropcap">The intersection of audience retention and organic discovery has reached a critical pivot point. As we analyze the trajectory of views against subscriber acquisition, we observe a decoupling of traditional metrics in favor of high-intensity engagement cycles.</p>
                            <p>A deep analytical dive into the traction of your latest creative endeavors suggests a shift toward short-form synthesis.</p>
                        </div>
                        <div className="mt-12 space-y-6">
                            <div className="flex items-center justify-between border-b border-border-soft pb-4 uppercase tracking-[0.2em] text-[10px] font-bold">
                                <span className="text-primary">Velocity Index</span>
                                <span className="serif-display italic text-lg text-charcoal tracking-normal normal-case">Accelerating</span>
                            </div>
                            <div className="flex items-center justify-between border-b border-border-soft pb-4 uppercase tracking-[0.2em] text-[10px] font-bold">
                                <span className="text-secondary">Retention Peak</span>
                                <span className="serif-display italic text-lg text-charcoal tracking-normal normal-case">84% At 2:40m</span>
                            </div>
                        </div>
                    </div>
                    <div className="lg:col-span-7 bg-white p-12 border border-border-soft paper-shadow">
                        <div className="flex justify-between items-start mb-12">
                            <p className="text-[9px] uppercase tracking-widest font-bold text-zinc-400">Fig. 01 — Retention Curve Analysis</p>
                            <div className="flex gap-4">
                                <div className="flex items-center gap-2 text-[9px] uppercase tracking-widest font-bold">
                                    <span className="w-3 h-px bg-primary"></span> Views
                                </div>
                                <div className="flex items-center gap-2 text-[9px] uppercase tracking-widest font-bold">
                                    <span className="w-3 h-px border-b border-dashed border-secondary"></span> Followers
                                </div>
                            </div>
                        </div>
                        <div className="h-[400px] w-full relative">
                            <PerformanceChart data={(videos || []).slice(0, 10).map((v: any) => ({
                                name: v.title.slice(0, 10),
                                views: v.views,
                                engagement: (v.engagement_rate || 0) * 100
                            }))} />
                            <div className="absolute bottom-[-30px] w-full flex justify-between text-[9px] font-bold text-zinc-400 tracking-[0.2em]">
                                <span>LATEST VIDEOS PERFORMANCE</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Semantic Landscape */}
            <section className="mb-32 border-y border-charcoal py-16 flex flex-col md:flex-row gap-16 items-center">
                <div className="md:w-1/3">
                    <h3 className="serif-display text-3xl font-bold mb-4">Semantic Landscape</h3>
                    <p className="text-sm text-zinc-500 leading-relaxed uppercase tracking-tighter font-medium">A typographic visualization of recurring themes and metadata clusters within the algorithmic ecosystem.</p>
                </div>
                <div className="md:w-2/3 flex flex-wrap gap-x-12 gap-y-6 items-center justify-center italic">
                    <span className="serif-display text-4xl font-light text-charcoal">AI Creation</span>
                    <span className="text-xs uppercase tracking-[0.5em] text-secondary font-bold">Tutorials</span>
                    <span className="serif-display text-7xl font-bold text-primary">Future</span>
                    <span className="serif-display text-3xl text-zinc-400">Minimalism</span>
                    <span className="text-xl uppercase tracking-tighter text-charcoal border-b border-charcoal font-black">Workflow</span>
                    <span className="serif-display text-6xl font-light text-secondary">Mastering</span>
                    <span className="serif-display text-5xl font-bold text-primary">Synthetics</span>
                </div>
            </section>

            {/* Recent Feed */}
            <section className="mb-32">
                <div className="flex items-end justify-between mb-16 px-2">
                    <div>
                        <span className="text-[10px] uppercase tracking-[0.4em] font-bold text-secondary block mb-2 font-black">Portfolio</span>
                        <h3 className="serif-display text-5xl font-bold">Recent Activity Feed</h3>
                    </div>
                    <button className="text-xs font-bold uppercase tracking-widest border-b border-zinc-300 pb-1 hover:border-charcoal transition-all">Full Archive</button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                    {videoStats.map((v: any, i: number) => (
                        <motion.article
                            key={v.title}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 * i }}
                            className="flex flex-col group"
                        >
                            <div className="aspect-[3/4] overflow-hidden mb-8 border border-border-soft transition-all duration-700">
                                <img src={v.image} alt={v.title} className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110" />
                            </div>
                            <div className="flex items-center gap-4 mb-4 uppercase tracking-widest text-[9px] font-bold">
                                <span className="text-secondary">{v.type}</span>
                                <span className="h-px flex-1 bg-border-soft" />
                                <span className="text-zinc-400">{v.time}</span>
                            </div>
                            <h4 className="serif-display text-3xl font-bold mb-6 group-hover:italic transition-all leading-tight">
                                {v.title}
                            </h4>
                            <div className="grid grid-cols-2 gap-8 pt-6 border-t border-charcoal">
                                <div>
                                    <p className="text-[9px] uppercase tracking-widest font-bold text-zinc-400 mb-1">Views</p>
                                    <p className="serif-display text-2xl font-black">{v.plays}</p>
                                </div>
                                <div>
                                    <p className="text-[9px] uppercase tracking-widest font-bold text-zinc-400 mb-1">CTR</p>
                                    <p className="serif-display text-2xl font-black">{v.ctr}</p>
                                </div>
                            </div>
                        </motion.article>
                    ))}
                </div>
            </section>

            {/* Performance Index Table */}
            <section className="mb-32">
                <div className="bg-white border-y-2 border-charcoal p-12 paper-shadow">
                    <h3 className="serif-display text-xl font-bold mb-12 text-center uppercase tracking-[0.4em] text-charcoal/80">Video Performance Index — Q3</h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="border-b border-charcoal">
                                    <th className="py-6 text-[10px] uppercase tracking-[0.3em] font-black">Metric Cluster</th>
                                    <th className="py-6 text-[10px] uppercase tracking-[0.3em] font-black">Current Volume</th>
                                    <th className="py-6 text-[10px] uppercase tracking-[0.3em] font-black text-center">Efficiency</th>
                                    <th className="py-6 text-[10px] uppercase tracking-[0.3em] font-black text-right">Momentum</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border-soft">
                                {tableData.map((row: any) => (
                                    <tr key={row.metric} className="group hover:bg-offwhite/50">
                                        <td className="py-8">
                                            <p className="serif-display text-xl font-bold italic">{row.metric}</p>
                                            <p className="text-[10px] text-zinc-400 uppercase tracking-widest mt-1 font-bold">{row.pathway}</p>
                                        </td>
                                        <td className="py-8 serif-display text-2xl font-black">{row.volume}</td>
                                        <td className="py-8 text-center text-primary">
                                            {row.status === 'viral' ? <Star fill="currentColor" /> : row.status === 'high' ? <TrendingUp /> : <BarChart2 />}
                                        </td>
                                        <td className="py-8 text-right serif-display text-lg text-secondary font-black">{row.momentum}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default YouTubeInsights;
