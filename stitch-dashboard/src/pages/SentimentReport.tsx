import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { BarChart3, MessageSquare, Heart, Share2, Quote, ArrowUpRight, Loader2, Youtube, TrendingUp } from 'lucide-react';
import { analyticsApi, Channel, Video, SentimentData, Comment } from '@/lib/api';
import { SentimentPieChart } from '@/components/ui/Charts';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

import { useCreator } from '@/context/CreatorContext';

const SentimentReport = () => {
    const { selectedCreatorId } = useCreator();
    const [selectedVideoIndex, setSelectedVideoIndex] = useState<number>(0);
    const channelId = selectedCreatorId;

    // Fetch channel info
    const { data: selectedChannel } = useQuery<Channel>({
        queryKey: ['youtube-metrics', channelId],
        queryFn: () => analyticsApi.getYoutubeMetrics(channelId!),
        enabled: !!channelId,
    });

    const { data: videos } = useQuery<Video[]>({
        queryKey: ['youtube-videos', channelId],
        queryFn: () => analyticsApi.getYoutubeVideos(channelId!),
        enabled: !!channelId,
    });

    const videoId = videos?.[selectedVideoIndex]?.video_id;
    const selectedVideo = videos?.[selectedVideoIndex];

    const { data: sentimentData, isLoading: sentimentLoading } = useQuery<SentimentData>({
        queryKey: ['sentiment', videoId],
        queryFn: () => analyticsApi.getVideoSentiment(videoId!),
        enabled: !!videoId,
    });

    if (sentimentLoading) {
        return (
            <div className="min-h-[60vh] flex items-center justify-center">
                <Loader2 className="w-12 h-12 text-primary animate-spin" />
            </div>
        );
    }

    const totalComments = sentimentData?.total_comments || 1;
    // Don't fallback to {} to preserve type info, handle undefined access instead
    const distribution = sentimentData?.sentiment_distribution;

    // Use ratios from backend if available, otherwise calculate
    const positivePercent = sentimentData?.positive_ratio !== undefined ? sentimentData.positive_ratio : ((distribution?.positive || 0) / totalComments * 100).toFixed(1);
    const neutralPercent = sentimentData?.neutral_ratio !== undefined ? sentimentData.neutral_ratio : ((distribution?.neutral || 0) / totalComments * 100).toFixed(1);
    const negativePercent = sentimentData?.negative_ratio !== undefined ? sentimentData.negative_ratio : ((distribution?.negative || 0) / totalComments * 100).toFixed(1);

    const legend = [
        { label: "Positive", value: positivePercent + "%", color: "bg-secondary" },
        { label: "Neutral", value: neutralPercent + "%", color: "bg-primary" },
        { label: "Negative", value: negativePercent + "%", color: "bg-zinc-300" }
    ];

    const pieData = [
        { name: 'Positive', value: distribution?.positive || 0, color: '#8ba88e' },
        { name: 'Neutral', value: distribution?.neutral || 0, color: '#2d6a6d' },
        { name: 'Negative', value: distribution?.negative || 0, color: '#c06c52' },
    ];

    const commentsList = sentimentData?.top_comments || sentimentData?.positive_examples || [];
    const comments = commentsList.slice(0, 4).map((c: Comment) => ({
        text: c.text,
        author: c.author || "Viewer",
        tag: c.label || "Key Insight",
        color: "border-primary"
    }));

    // Use real videos for activities
    const activities = (videos || []).slice(0, 3).map((v: Video) => ({
        title: v.title?.slice(0, 50) || "Video Title",
        desc: v.description ? (v.description.slice(0, 120) + "...") : "No description available.",
        stats: ((v.engagement_rate || 0) * 100).toFixed(1) + "% Eng.",
        label: "YouTube Video",
        color: "text-primary",
        image: v.thumbnail_url || "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400&h=300&fit=crop"
    }));

    return (
        <div className="animate-fade-in">
            <header className="mb-24">
                <div className="grid lg:grid-cols-12 gap-12 border-b border-charcoal pb-12">
                    <div className="lg:col-span-8">
                        <span className="text-[10px] uppercase tracking-[0.4em] text-secondary font-black mb-6 block italic underline decoration-charcoal/20 underline-offset-8">Volume IX • Research Report</span>
                        <motion.h2
                            initial={{ opacity: 0, x: -50 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="serif-display text-7xl lg:text-[10rem] font-black leading-[0.85] tracking-tighter mb-8"
                        >
                            Audience <br />Sentiment <span className="italic text-primary">Report</span>
                        </motion.h2>
                        <div className="flex items-start gap-12 max-w-2xl">
                            <p className="text-xl leading-relaxed text-charcoal/80 font-medium italic serif-display border-l-4 border-secondary pl-6">
                                An exhaustive linguistic deconstruction of community engagement. We examine the shift from passive observation to active emotional investment across digital touchpoints.
                            </p>
                            {selectedChannel && (
                                <div className="flex flex-col gap-1 shrink-0">
                                    <span className="text-[10px] uppercase font-black tracking-widest text-muted-gray">Analyzing</span>
                                    <div className="flex items-center gap-2 border-b border-charcoal pb-1">
                                        <img
                                            src={selectedChannel.thumbnail_url || 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=40&h=40&fit=crop&crop=face'}
                                            alt={selectedChannel.title}
                                            className="w-6 h-6 rounded-full object-cover"
                                        />
                                        <span className="text-xs font-black uppercase tracking-widest truncate max-w-[120px]">{selectedChannel.title}</span>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                    <div className="lg:col-span-4 flex flex-col justify-end">
                        <motion.div
                            whileHover={{ rotate: -1, scale: 1.02 }}
                            className="bg-border-soft p-10 aspect-square flex flex-col justify-between paper-shadow border border-charcoal/5"
                        >
                            <div>
                                <BarChart3 size={48} className="mb-6 text-primary" />
                                <h3 className="serif-display text-4xl font-black italic leading-tight">Sentiment Volatility</h3>
                            </div>
                            <div>
                                <p className="text-[10px] uppercase tracking-[0.2em] font-black mb-2 text-charcoal/60">Primary Driver</p>
                                <p className="text-5xl font-black serif-display text-primary">+12.4%</p>
                                <p className="text-xs mt-4 opacity-70 leading-relaxed font-bold tracking-tight">Net positive shifts in technical discussion threads over the last fiscal quarter.</p>
                            </div>
                        </motion.div>
                    </div>
                </div>
            </header>

            {/* Chart Section */}
            <section className="mb-32">
                <div className="grid lg:grid-cols-12 gap-16">
                    <div className="lg:col-span-3 flex flex-col justify-between py-4">
                        <div className="space-y-12">
                            <div>
                                <h3 className="text-[10px] uppercase tracking-widest font-black border-b border-black pb-4 mb-8">Legend Index</h3>
                                <ul className="space-y-8">
                                    {legend.map(l => (
                                        <li key={l.label} className="flex items-center justify-between group">
                                            <span className="flex items-center gap-3 text-xs font-black uppercase tracking-widest group-hover:text-primary transition-colors">
                                                <span className={`w-3 h-3 ${l.color}`}></span> {l.label}
                                            </span>
                                            <span className="serif-display font-black text-lg">{l.value}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div className="p-8 bg-white border border-border-soft paper-shadow italic font-medium serif-display text-sm leading-relaxed text-charcoal/70">
                                "The linguistic markers suggest a maturing audience profile that prioritizes utility over novelty."
                            </div>
                        </div>
                    </div>
                    <div className="lg:col-span-9">
                        <div className="relative h-[550px] w-full border-l border-b border-charcoal p-12 bg-[#fcfaf7]">
                            <SentimentPieChart data={pieData} />
                            <div className="absolute -bottom-10 w-full flex justify-between text-[10px] font-black uppercase tracking-[0.3em] text-muted-gray">
                                <span>Sentiment Distribution Analysis</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Activities Grid */}
            <section className="mb-32">
                <div className="flex items-center gap-8 mb-16">
                    <h3 className="serif-display text-5xl font-black italic">Recent Activity</h3>
                    <div className="flex-grow h-[1px] bg-charcoal/10" />
                    <button className="text-[10px] font-black uppercase tracking-widest border border-charcoal px-8 py-3 hover:bg-black hover:text-white transition-all">View Archive</button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-16">
                    {activities.map((art: any, i: number) => (
                        <motion.article
                            key={art.title}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 * i }}
                            className="group cursor-pointer"
                        >
                            <div className="aspect-[16/10] overflow-hidden mb-10 border border-border-soft paper-shadow transition-all duration-700">
                                <img src={art.image} alt={art.title} className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110" />
                            </div>
                            <div className="space-y-6">
                                <div className="flex items-center justify-between border-b border-border-soft pb-4">
                                    <span className={`text-[10px] font-black uppercase tracking-[0.3em] ${art.color}`}>{art.label}</span>
                                    <span className="text-[9px] font-bold uppercase tracking-widest text-muted-gray italic">Recent Dispatch</span>
                                </div>
                                <h4 className="serif-display text-3xl font-black leading-tight group-hover:italic transition-all">{art.title}</h4>
                                <p className="text-sm leading-relaxed text-charcoal/70 font-medium serif-display italic">{art.desc}</p>
                                <div className="grid grid-cols-2 gap-8 py-6 border-t border-border-soft">
                                    <div>
                                        <p className="text-[9px] uppercase tracking-widest font-black text-muted-gray mb-1">Impact Score</p>
                                        <p className="text-2xl font-black serif-display italic text-primary">{art.stats}</p>
                                    </div>
                                    <div className="flex items-end justify-end">
                                        <ArrowUpRight className={`w-8 h-8 ${art.color} group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform`} />
                                    </div>
                                </div>
                            </div>
                        </motion.article>
                    ))}
                </div>
            </section>

            {/* Explorer Section */}
            <section className="mt-40 border-t border-charcoal pt-24 mb-32">
                <div className="grid lg:grid-cols-12 gap-20">
                    <div className="lg:col-span-4">
                        <h3 className="serif-display text-6xl font-black mb-8 italic">Comment <br />Explorer</h3>
                        <p className="text-xl font-medium leading-relaxed mb-12 italic serif-display text-charcoal/70">A curated selection of the most philosophically relevant feedback from the past 30 days.</p>
                        <div className="space-y-6">
                            <div className="flex items-center gap-4">
                                <span className="w-12 h-[1px] bg-secondary"></span>
                                <span className="text-[10px] uppercase font-black tracking-widest">Sentiment Density</span>
                            </div>
                            <div className="h-3 w-full bg-border-soft relative overflow-hidden">
                                <div className="absolute left-0 top-0 h-full bg-secondary transition-all" style={{ width: `${positivePercent}%` }} />
                                <div className="absolute top-0 h-full bg-primary transition-all" style={{ left: `${positivePercent}%`, width: `${neutralPercent}%` }} />
                            </div>
                            <div className="flex justify-between text-[10px] font-black uppercase tracking-widest opacity-50">
                                <span>Positive ({positivePercent}%)</span>
                                <span>Inquisitive ({neutralPercent}%)</span>
                            </div>
                        </div>
                    </div>
                    <div className="lg:col-span-8 grid md:grid-cols-2 gap-12">
                        {comments.map((c: any, i: number) => (
                            <motion.div
                                key={c.author}
                                initial={{ opacity: 0, x: 30 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.1 * i }}
                                className={`p-10 border-l-8 ${c.color} bg-white paper-shadow flex flex-col justify-between`}
                            >
                                <div>
                                    <Quote size={32} className="text-muted-gray/20 mb-6" />
                                    <p className="text-xl serif-display font-medium italic leading-relaxed mb-8 text-charcoal/90">"{c.text}"</p>
                                </div>
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-full bg-border-soft flex items-center justify-center font-black serif-display border border-charcoal/10">
                                        {c.author[0]}
                                    </div>
                                    <div>
                                        <span className="text-xs font-black uppercase tracking-widest block">{c.author}</span>
                                        <span className="text-[9px] font-bold italic opacity-50 uppercase tracking-widest">{c.tag}</span>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>
        </div>
    );
};

export default SentimentReport;
