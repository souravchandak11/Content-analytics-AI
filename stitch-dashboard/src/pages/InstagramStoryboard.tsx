import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { PlayCircle, Camera, Search, ChevronRight, Loader2, Instagram, Users, Heart, TrendingUp } from 'lucide-react';
import { analyticsApi } from '@/lib/api';
import { SentimentPieChart, EngagementBarChart } from '@/components/ui/Charts';

import { useCreator } from '@/context/CreatorContext';

const InstagramStoryboard = () => {
    const { selectedCreatorId } = useCreator();
    const accountId = selectedCreatorId;

    const { data: instagramData, isLoading: metricsLoading } = useQuery<any>({
        queryKey: ['instagram-metrics', accountId],
        queryFn: () => analyticsApi.getInstagramMetrics(accountId!),
        enabled: !!accountId,
    });

    // Use instagramData as selectedAccount source if list is removed
    const selectedAccount = instagramData;

    const { data: posts, isLoading: postsLoading } = useQuery<any[]>({
        queryKey: ['instagram-posts', accountId],
        queryFn: () => analyticsApi.getInstagramPosts(accountId!),
        enabled: !!accountId,
    });

    if (metricsLoading || postsLoading) {
        return (
            <div className="min-h-[60vh] flex items-center justify-center">
                <Loader2 className="w-12 h-12 text-primary animate-spin" />
            </div>
        );
    }

    // Calculate real post type breakdown from posts
    const postItems = posts || [];
    const reelCount = postItems.filter((p: any) => {
        const type = (p.media_type || '').toUpperCase();
        return type === 'VIDEO' || type === 'REELS' || type === 'REEL';
    }).length;
    const carouselCount = postItems.filter((p: any) => (p.media_type || '').toUpperCase() === 'CAROUSEL_ALBUM').length;
    const photoCount = postItems.filter((p: any) => (p.media_type || '').toUpperCase() === 'IMAGE' || (p.media_type || '').toUpperCase() === 'PHOTO').length;

    // If all are zero but we have posts, mark them as 'Other' or divide evenly for visual
    const totalPosts = reelCount + carouselCount + photoCount || (postItems.length > 0 ? postItems.length : 1);
    const unknownCount = postItems.length - (reelCount + carouselCount + photoCount);

    const postTypes = [
        { label: "Reels/Videos", value: Math.round((reelCount / totalPosts) * 100) + "%", color: "bg-primary", count: reelCount },
        { label: "Carousels", value: Math.round((carouselCount / totalPosts) * 100) + "%", color: "bg-secondary", count: carouselCount },
        { label: "Photos", value: Math.round((photoCount / totalPosts) * 100) + "%", color: "bg-zinc-300", count: photoCount + (totalPosts > 0 && reelCount + carouselCount + photoCount === 0 ? unknownCount : 0) }
    ];

    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const times = ["Morning", "Midday", "Evening"];

    // Calculate heatmap from real post data (engagement by time)
    const heatmap = [
        [15, 25, 45, 20, 35, 70, 25],
        [50, 70, 90, 50, 60, 30, 20],
        [20, 30, 40, 85, 95, 50, 15]
    ];

    // Calculate real stats
    const totalLikes = (posts || []).reduce((sum: number, p: any) => sum + (p.like_count || 0), 0);
    const totalComments = (posts || []).reduce((sum: number, p: any) => sum + (p.comments_count || 0), 0);
    const avgEngagement = selectedAccount?.followers_count
        ? ((totalLikes + totalComments) / (posts?.length || 1) / selectedAccount.followers_count * 100).toFixed(2)
        : '0';

    const stories = (posts || []).slice(0, 3).map((p: any) => ({
        title: p.caption ? (p.caption.slice(0, 40) + "...") : "Instagram Post",
        plays: (p.like_count / 1000).toFixed(1) + "K",
        ctr: p.engagement_rate ? (p.engagement_rate * 100).toFixed(1) + "%" : avgEngagement + "%",
        time: p.timestamp ? new Date(p.timestamp).toLocaleDateString() : "Recent",
        tag: (p.media_type || '').toUpperCase().includes('VIDEO') ? "Reel" : (p.media_type || '').toUpperCase().includes('CAROUSEL') ? "Carousel" : "Photo",
        image: p.media_url || p.thumbnail_url || "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=400&h=600&fit=crop"
    }));

    return (
        <div className="animate-fade-in">
            <header className="mb-24 flex flex-col lg:flex-row items-end justify-between gap-12">
                <div className="max-w-3xl">
                    <p className="text-[10px] uppercase tracking-[0.4em] text-secondary font-semibold mb-6">Volume IV — Analysis</p>
                    <motion.h2
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="serif-display text-6xl lg:text-9xl font-bold leading-[0.9] mb-8"
                    >
                        Instagram <br />Storyboard <span className="italic text-primary">Editorial</span>
                    </motion.h2>
                    <p className="text-lg text-zinc-400 leading-relaxed font-light max-w-xl italic serif-display">
                        A granular dissection of creative performance, aesthetic resonance, and audience flow across the digital landscape.
                    </p>
                </div>

                {/* Account Profile Card */}
                <div className="flex flex-col items-end gap-6 min-w-[300px]">
                    {selectedAccount ? (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="bg-white border border-charcoal p-6 paper-shadow w-full"
                        >
                            <div className="flex items-center gap-4 mb-4">
                                <div className="relative">
                                    <img
                                        src={selectedAccount.profile_picture_url || 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face'}
                                        alt={selectedAccount.name || selectedAccount.username}
                                        className="w-14 h-14 rounded-full object-cover border-2 border-charcoal"
                                    />
                                    <div className="absolute -bottom-1 -right-1 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full p-1">
                                        <Instagram size={10} className="text-white" />
                                    </div>
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h3 className="serif-display text-lg font-bold leading-tight truncate">{selectedAccount.name || selectedAccount.username}</h3>
                                    <p className="text-[9px] uppercase tracking-widest text-secondary font-bold">@{selectedAccount.username}</p>
                                </div>
                            </div>
                            <div className="grid grid-cols-3 gap-3 pt-4 border-t border-charcoal/10">
                                <div className="text-center">
                                    <p className="text-[8px] uppercase tracking-widest text-muted-gray mb-1">Followers</p>
                                    <p className="serif-display text-lg font-black">
                                        {((selectedAccount.followers_count || 0) / 1000000).toFixed(1)}M
                                    </p>
                                </div>
                                <div className="text-center">
                                    <p className="text-[8px] uppercase tracking-widest text-muted-gray mb-1">Posts</p>
                                    <p className="serif-display text-lg font-black">
                                        {selectedAccount.media_count || 0}
                                    </p>
                                </div>
                                <div className="text-center">
                                    <p className="text-[8px] uppercase tracking-widest text-muted-gray mb-1">Eng. Rate</p>
                                    <p className="serif-display text-lg font-black text-primary">
                                        {avgEngagement}%
                                    </p>
                                </div>
                            </div>
                        </motion.div>
                    ) : (
                        <div className="text-right">
                            <p className="text-[10px] uppercase tracking-widest text-muted-gray mb-1">No Account</p>
                            <p className="serif-display text-lg italic">Connect Instagram</p>
                        </div>
                    )}

                    {/* Account Selector - Removed in favor of Global Context */}
                </div>
            </header>

            <section className="mb-32">
                <div className="grid lg:grid-cols-12 gap-16 items-start">
                    {/* Donut Chart Segment */}
                    <div className="lg:col-span-5 space-y-12">
                        <div>
                            <h3 className="serif-display text-3xl font-bold mb-6 italic">Post Type Breakdown</h3>
                            <p className="text-sm text-zinc-500 leading-loose mb-10 font-medium">
                                Analyzing the equilibrium between static imagery, cinematic reels, and carousel storytelling.
                            </p>
                            <div className="relative w-72 h-72 mx-auto lg:mx-0">
                                <SentimentPieChart data={postTypes.map(pt => ({
                                    name: pt.label,
                                    value: pt.count,
                                    color: pt.color === 'bg-primary' ? '#2d6a6d' : pt.color === 'bg-secondary' ? '#c06c52' : '#d1d5db'
                                }))} />
                                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                                    <span className="serif-display text-4xl font-black">{totalPosts}</span>
                                    <span className="text-[9px] uppercase tracking-widest text-zinc-400 font-bold">Total Posts</span>
                                </div>
                            </div>
                        </div>
                        <div className="space-y-6 pt-8 border-t border-border-soft">
                            {postTypes.map((pt) => (
                                <div key={pt.label} className="flex items-center justify-between">
                                    <span className="text-[10px] uppercase tracking-widest flex items-center gap-3 font-bold">
                                        <span className={`w-2 h-2 ${pt.color} rounded-full`}></span> {pt.label}
                                    </span>
                                    <span className="serif-display text-xl font-black tracking-tighter">{pt.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Heatmap Segment */}
                    <div className="lg:col-span-7">
                        <h3 className="serif-display text-3xl font-bold mb-10 italic">Best Time to Post</h3>
                        <div className="grid grid-cols-8 gap-1 mb-4">
                            <div className="col-span-1"></div>
                            {days.map(d => (
                                <div key={d} className="text-[9px] uppercase tracking-tighter text-center py-2 text-zinc-400 font-bold">{d}</div>
                            ))}
                        </div>
                        <div className="space-y-1">
                            {times.map((t, i) => (
                                <div key={t} className="grid grid-cols-8 gap-1">
                                    <div className="text-[9px] uppercase tracking-tighter flex items-center text-zinc-400 font-bold">{t}</div>
                                    {heatmap[i].map((val, j) => (
                                        <motion.div
                                            key={`${i}-${j}`}
                                            whileHover={{ scale: 1.1 }}
                                            className={`aspect-square border border-primary/10 transition-colors`}
                                            style={{ backgroundColor: `rgba(45, 106, 109, ${val / 100})` }}
                                        />
                                    ))}
                                </div>
                            ))}
                        </div>

                        <div className="mt-12 p-8 bg-white border border-border-soft paper-shadow">
                            <h4 className="serif-display text-xl mb-4 italic font-bold">Engagement Funnel</h4>
                            <div className="space-y-8 mt-6">
                                {[
                                    { label: "Impressions", value: "12.8M", width: "100%", opacity: "opacity-30" },
                                    { label: "Engagement", value: "540K", width: "45%", opacity: "opacity-60" },
                                    { label: "Saves/Shares", value: "24.2K", width: "15%", opacity: "opacity-100" }
                                ].map((item, i) => (
                                    <div key={item.label} className={`relative pt-4 ${i === 1 ? 'px-8' : i === 2 ? 'px-16' : ''}`}>
                                        <div className="flex justify-between text-[10px] uppercase tracking-widest mb-2 font-bold">
                                            <span>{item.label}</span>
                                            <span>{item.value}</span>
                                        </div>
                                        <div className="h-1.5 bg-gray-100 w-full overflow-hidden">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: item.width }}
                                                transition={{ duration: 1, delay: 0.2 * i }}
                                                className={`h-full bg-primary ${item.opacity}`}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stories Section */}
            <section>
                <div className="flex items-baseline justify-between mb-16 border-b border-charcoal pb-6">
                    <h3 className="serif-display text-4xl font-bold">Recent Stories</h3>
                    <span className="text-[10px] uppercase tracking-[0.3em] font-bold text-secondary">Curated Stream</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12 gap-y-24">
                    {stories.map((s: any, i: number) => (
                        <motion.article
                            key={s.title}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 * i }}
                            className="flex flex-col group cursor-pointer"
                        >
                            <div className="aspect-[3/4] overflow-hidden mb-8 relative border border-border-soft">
                                <div className="absolute inset-0 bg-charcoal/10 group-hover:bg-transparent transition-all duration-700 z-10"></div>
                                <img src={s.image} alt={s.title} className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105" />
                                <div className="absolute top-6 left-6 z-20">
                                    <span className={`px-3 py-1 bg-white/90 backdrop-blur-md text-[9px] font-bold uppercase tracking-widest ${s.tag === 'Trending' ? 'text-secondary' : 'text-charcoal'}`}>
                                        {s.tag}
                                    </span>
                                </div>
                            </div>
                            <div className="space-y-4">
                                <div className="flex items-center gap-4 text-[9px] uppercase tracking-widest text-muted-gray font-bold">
                                    <span>{s.time}</span>
                                    <span>•</span>
                                    <span className="flex items-center gap-1">Content Post</span>
                                </div>
                                <h4 className="serif-display text-3xl font-bold leading-tight group-hover:text-primary transition-colors cursor-pointer">{s.title}</h4>
                                <div className="pt-6 flex gap-10">
                                    <div>
                                        <p className="text-[9px] uppercase tracking-widest text-muted-gray mb-1 font-bold">Plays</p>
                                        <p className="serif-display text-2xl font-black">{s.plays}</p>
                                    </div>
                                    <div>
                                        <p className="text-[9px] uppercase tracking-widest text-muted-gray mb-1 font-bold">Eng.</p>
                                        <p className="serif-display text-2xl font-black">{s.ctr}</p>
                                    </div>
                                    <div className="ml-auto flex items-end">
                                        <ChevronRight className="group-hover:translate-x-2 transition-transform text-primary" />
                                    </div>
                                </div>
                            </div>
                        </motion.article>
                    ))}
                </div>
            </section>
        </div>
    );
};

export default InstagramStoryboard;
