import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Sparkles, TrendingUp, BarChart, Zap, ChevronRight, Loader2, Youtube, Target, Activity } from 'lucide-react';
import { analyticsApi } from '@/lib/api';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

import { useCreator } from '@/context/CreatorContext';

const PredictiveIntelligence = () => {
    const { selectedCreatorId } = useCreator();
    const channelId = selectedCreatorId;

    // Fetch channel details (assuming metrics endpoint gives us Channel info)
    const { data: selectedChannel, isLoading: channelLoading } = useQuery<any>({
        queryKey: ['youtube-metrics', channelId],
        queryFn: () => analyticsApi.getYoutubeMetrics(channelId!),
        enabled: !!channelId,
    });

    const { data: forecast, isLoading } = useQuery<any>({
        queryKey: ['forecast', channelId],
        queryFn: () => analyticsApi.forecastSubscribers(channelId!),
        enabled: !!channelId,
    });

    if (isLoading) {
        return (
            <div className="min-h-[60vh] flex items-center justify-center">
                <Loader2 className="w-12 h-12 text-primary animate-spin" />
            </div>
        );
    }

    // Simulation State
    const [simParams, setSimParams] = useState({
        frequency: 1, // 1.0 = baseline (e.g. 3 posts/week)
        adSpend: 1,   // 1.0 = baseline ($1.2k)
        sentiment: 1  // 1.0 = baseline (Positive)
    });

    // Simulation effect multipliers (simplified model)
    // Frequency: +20% growth per +1x frequency
    // Ad Spend: +15% growth per +1x spend
    // Sentiment: +30% growth per +1x sentiment score
    const calculateSimulationMultiplier = () => {
        const freqEffect = (simParams.frequency - 1) * 0.2;
        const adEffect = (simParams.adSpend - 1) * 0.15;
        const sentEffect = (simParams.sentiment - 1) * 0.3;
        return 1 + freqEffect + adEffect + sentEffect;
    };

    const simMultiplier = calculateSimulationMultiplier();

    // Transform forecast data for Recharts with Simulation
    const chartData = (forecast?.forecast?.slice(0, 12) || []).map((f: any, i: number) => {
        const date = new Date(f.date || f.ds);
        const baselineValue = Math.round(f.predicted || f.yhat || 0);

        // Apply cumulative compound effect for simulation to show divergence over time
        // We use 'i' to simulate time-based compounding
        const timeFactor = 1 + (i * 0.05);
        const simulatedValue = Math.round(baselineValue * (1 + ((simMultiplier - 1) * timeFactor)));

        return {
            name: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            value: baselineValue,             // Original
            simulated: simulatedValue,        // New Simulated series
            upper: Math.round(f.upper_bound || f.yhat_upper || 0),
            lower: Math.round(f.lower_bound || f.yhat_lower || 0)
        };
    });

    // Calculate growth metrics based on SIMULATION
    const currentSubs = selectedChannel?.subscribers || forecast?.forecast?.[0]?.yhat || 0;
    const originalPredictedSubs = forecast?.forecast?.[forecast?.forecast?.length - 1]?.yhat || currentSubs;
    const simulatedPredictedSubs = chartData.length > 0 ? chartData[chartData.length - 1].simulated : originalPredictedSubs;

    // Display growth of the SIMULATED outcome
    const growthPercent = (currentSubs > 0 && simulatedPredictedSubs > 0)
        ? ((simulatedPredictedSubs - currentSubs) / currentSubs * 100).toFixed(1)
        : "0.0";
    const growthDelta = simulatedPredictedSubs - originalPredictedSubs; // Difference caused by simulation

    const simulationSliders = [
        {
            label: "Post Frequency",
            value: simParams.frequency,
            display: `${(3 * simParams.frequency).toFixed(0)} / Week`,
            min: 0.5, max: 3.0, step: 0.5,
            param: 'frequency'
        },
        {
            label: "Ad Spend Intensity",
            value: simParams.adSpend,
            display: `$${(1.2 * simParams.adSpend).toFixed(1)}k`,
            min: 0, max: 5.0, step: 0.5,
            param: 'adSpend'
        },
        {
            label: "Audience Sentiment",
            value: simParams.sentiment,
            display: simParams.sentiment > 1.2 ? "Viral" : simParams.sentiment > 0.8 ? "Positive" : "Neutral",
            min: 0.5, max: 1.5, step: 0.1,
            param: 'sentiment'
        }
    ];

    return (
        <div className="animate-fade-in">
            <header className="mb-24 grid lg:grid-cols-12 gap-12">
                <div className="lg:col-span-8 border-b border-charcoal pb-12">
                    <p className="text-[10px] uppercase tracking-[0.4em] font-black text-secondary mb-6 italic">Issue No. 04 — The Algorithms of Tomorrow</p>
                    <motion.h2
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="serif-display text-7xl lg:text-9xl font-bold leading-none tracking-tight"
                    >
                        Predictive <br /><span className="italic text-primary">Intelligence</span>
                    </motion.h2>
                </div>

                {/* Channel Profile Card */}
                <div className="lg:col-span-4 flex flex-col justify-end">
                    {selectedChannel ? (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="bg-white border border-charcoal p-6 paper-shadow"
                        >
                            <div className="flex items-center gap-4 mb-4">
                                <div className="relative">
                                    <img
                                        src={selectedChannel.thumbnail_url || 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face'}
                                        alt={selectedChannel.title}
                                        className="w-12 h-12 rounded-full object-cover border-2 border-charcoal"
                                    />
                                    <div className="absolute -bottom-1 -right-1 bg-red-600 rounded-full p-1">
                                        <Youtube size={8} className="text-white" />
                                    </div>
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h3 className="serif-display text-base font-bold leading-tight truncate">{selectedChannel.title}</h3>
                                    <p className="text-[9px] uppercase tracking-widest text-secondary font-bold">Forecasting</p>
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-3 pt-3 border-t border-charcoal/10">
                                <div>
                                    <p className="text-[8px] uppercase tracking-widest text-muted-gray mb-1">Current Subs</p>
                                    <p className="serif-display text-lg font-black">{(currentSubs / 1000000).toFixed(1)}M</p>
                                </div>
                                <div>
                                    <p className="text-[8px] uppercase tracking-widest text-muted-gray mb-1">Growth Est.</p>
                                    <p className="serif-display text-lg font-black text-primary">+{growthPercent}%</p>
                                </div>
                            </div>
                        </motion.div>
                    ) : (
                        <div className="text-right">
                            <p className="text-[10px] uppercase tracking-widest text-muted-gray mb-1">No Channel</p>
                            <p className="serif-display text-lg italic">Select a channel</p>
                        </div>
                    )}

                    {/* Channel Selector - Removed in favor of Global Context */}
                </div>
            </header>

            <div className="grid lg:grid-cols-12 gap-12 mb-32">
                {/* Forecast Chart */}
                <div className="lg:col-span-8">
                    <div className="relative w-full bg-[#f2f1ed] p-8 border border-border-soft paper-shadow flex flex-col overflow-hidden">
                        <div className="flex justify-between items-center mb-8">
                            <h3 className="serif-display text-3xl italic font-bold">Subscriber Forecast</h3>
                            <div className="flex gap-6 items-center">
                                <span className="text-[9px] uppercase tracking-widest text-muted-gray flex items-center gap-2 font-bold">
                                    <span className="w-2 h-[1px] bg-primary"></span> Predicted Growth
                                </span>
                                <span className="text-[9px] uppercase tracking-widest text-muted-gray flex items-center gap-2 font-bold">
                                    <span className="w-4 h-3 bg-primary/10"></span> Confidence Band
                                </span>
                            </div>
                        </div>

                        <div className="h-[300px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#2d6a6d" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#2d6a6d" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#8ba88e" stopOpacity={0.2} />
                                            <stop offset="95%" stopColor="#8ba88e" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                                    <XAxis
                                        dataKey="name"
                                        tick={{ fontSize: 10, fontWeight: 600 }}
                                        axisLine={{ stroke: '#333' }}
                                    />
                                    <YAxis
                                        tick={{ fontSize: 10 }}
                                        tickFormatter={(value) => (value / 1000000).toFixed(0) + 'M'}
                                        axisLine={{ stroke: '#333' }}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: '#fff',
                                            border: '1px solid #333',
                                            fontFamily: 'serif'
                                        }}
                                        formatter={(value: any) => {
                                            if (typeof value === 'number') {
                                                return [(value / 1000000).toFixed(2) + 'M', 'Subscribers'];
                                            }
                                            return [value, 'Subscribers'];
                                        }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="value"
                                        stroke="#8ba88e"
                                        strokeWidth={1}
                                        strokeDasharray="5 5"
                                        fill="url(#colorConfidence)"
                                        name="Baseline"
                                        animationDuration={1000}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="simulated"
                                        stroke="#2d6a6d"
                                        strokeWidth={3}
                                        fill="url(#colorForecast)"
                                        name="Simulated"
                                        animationDuration={500}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    <div className="mt-12 grid md:grid-cols-2 gap-12">
                        <p className="text-sm leading-relaxed text-charcoal/70 serif-display italic font-medium">
                            Adjust the simulation parameters to see how strategic shifts impact your projected growth.
                            {growthDelta > 0 && <span className="text-primary font-bold block mt-2">Simulation projects an additional +{(growthDelta / 1000000).toFixed(2)}M subscribers.</span>}
                        </p>
                        <div className="flex flex-col justify-end">
                            <div className="flex items-center gap-4 text-sm font-bold border-t border-charcoal pt-6">
                                <span className="serif-display italic text-3xl text-primary">01</span>
                                <span className="uppercase tracking-widest text-[10px] font-black">Statistical Reliability: 94.2%</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Probability Meter & Simulators */}
                <div className="lg:col-span-4 space-y-12">
                    <div className="border border-border-soft p-12 bg-white flex flex-col items-center justify-center text-center paper-shadow">
                        <p className="text-[10px] uppercase tracking-[0.2em] mb-12 font-black text-secondary">Virality Probability</p>
                        <div className="relative w-48 h-48">
                            <svg className="w-full h-full transform -rotate-90">
                                <circle cx="96" cy="96" fill="none" r="80" stroke="#f3f4f6" strokeWidth="2" />
                                <motion.circle
                                    initial={{ strokeDashoffset: 502 }}
                                    animate={{ strokeDashoffset: 502 - (502 * (0.75 * simMultiplier > 1 ? 1 : 0.75 * simMultiplier)) }}
                                    transition={{ duration: 1, ease: "easeOut" }}
                                    cx="96" cy="96" fill="none" r="80" stroke="#c06c52" strokeDasharray="502" strokeWidth="4"
                                />
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className="serif-display text-5xl font-black">{Math.min(100, Math.round(75 * simMultiplier))}<span className="text-2xl">%</span></span>
                                <span className="text-[8px] uppercase tracking-widest mt-2 text-secondary font-black">
                                    {simMultiplier > 1.1 ? "Very High" : "High Potential"}
                                </span>
                            </div>
                        </div>
                        <p className="mt-12 serif-display italic text-base text-muted-gray font-medium">"A calculated risk worth taking."</p>
                    </div>

                    <div className="space-y-8 p-10 bg-offwhite border border-charcoal">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.3em] border-b border-charcoal pb-4 mb-8">Simulation Engine</h4>
                        {simulationSliders.map(s => (
                            <div key={s.label} className="space-y-4">
                                <div className="flex justify-between text-[10px] uppercase tracking-widest font-black">
                                    <span className="text-charcoal/60">{s.label}</span>
                                    <span className="text-primary">{s.display}</span>
                                </div>
                                <input
                                    type="range"
                                    min={s.min}
                                    max={s.max}
                                    step={s.step}
                                    value={s.value}
                                    onChange={(e) => setSimParams(prev => ({ ...prev, [s.param]: parseFloat(e.target.value) }))}
                                    className="w-full h-1 bg-charcoal/10 rounded-lg appearance-none cursor-pointer accent-primary"
                                />
                            </div>
                        ))}
                        <button
                            onClick={() => setSimParams({ frequency: 1, adSpend: 1, sentiment: 1 })}
                            className="w-full py-4 bg-charcoal text-white text-[10px] font-black uppercase tracking-[0.3em] hover:bg-primary transition-colors flex items-center justify-center gap-2"
                        >
                            Reset Logic <Zap size={14} />
                        </button>
                    </div>
                </div>
            </div>

            {/* Archive Grid */}
            <section>
                <div className="flex items-baseline justify-between border-b border-charcoal pb-6 mb-16">
                    <h3 className="serif-display text-5xl font-bold italic">The Archive</h3>
                    <span className="text-[10px] uppercase tracking-widest font-black text-secondary">Recent Intelligence Units</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-12 gap-16">
                    <article className="md:col-span-7 group cursor-pointer pb-16">
                        <div className="aspect-[16/9] overflow-hidden mb-10 border border-border-soft paper-shadow">
                            <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuBR7PxzrvNNe0FV2QP35pVuzmjLwecW4-gAykjtWdaOagpJKXe4cmQerr-OISRzwThPIcqPKmh2vhsHc-rQs6t8a0u23MGxz8xJPuYE71t8Syai5xkG8NT27O_o4G2W8Kct6rmUrISZYPtn1OR3xLVkpgL_hkhBWWfNgQFOwO-kQk918kWavlIN_G4Yzndiqk0AJyUh1FGeIx_AJuEDOqFWGhh2tQb9nY3AmAvwLmlFSH93aX5E6sHIQsnGoHeYZFZ7haM1xIXg23dB" className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105" alt="AI Feature" />
                        </div>
                        <div className="flex items-center gap-4 mb-6 font-black uppercase tracking-[0.3em] text-[9px]">
                            <Sparkles size={14} className="text-primary" />
                            <span className="text-primary">Intelligence Report</span>
                            <span className="text-muted-gray">— 4h ago</span>
                        </div>
                        <h4 className="serif-display text-4xl font-black leading-tight mb-6 group-hover:text-primary transition-colors">The Future of AI Content Creation: A Predictive Model</h4>
                        <p className="text-lg leading-relaxed text-charcoal/70 serif-display italic font-medium mb-10">
                            Analyzing the intersection of generative tools and human creativity in the next fiscal quarter.
                        </p>
                        <div className="flex gap-12 border-t border-charcoal/10 pt-8">
                            <div>
                                <p className="text-[9px] uppercase tracking-widest font-black text-muted-gray mb-1">Predicted Reach</p>
                                <p className="serif-display text-2xl font-black italic">2.4M</p>
                            </div>
                            <div>
                                <p className="text-[9px] uppercase tracking-widest font-black text-muted-gray mb-1">Impact Score</p>
                                <p className="serif-display text-2xl font-black italic">8.9 / 10</p>
                            </div>
                            <div className="ml-auto flex items-end">
                                <ChevronRight className="group-hover:translate-x-3 transition-transform text-primary" size={32} />
                            </div>
                        </div>
                    </article>

                    <div className="md:col-span-5 grid grid-cols-1 gap-16">
                        {[
                            {
                                tag: "Visual Analysis",
                                title: "Morning Workspace: Aesthetic vs Performance",
                                stats: "118K Plays Est.",
                                image: "https://lh3.googleusercontent.com/aida-public/AB6AXuBr3f3ndFxDWzqSNVoQ_wXpfUHwEbzq9UazARTM09hu46kKlUlzceOiS4uonaa7kMG-XLp6QIhUE41C6wohqxmRychAVGwcBI9XiEsO6c6Ul0_UOrLJnVqwj_Q4AhtWKTWh3YP9a45NSUggYA_8LV6zkJZNoSHyJjRwfQ0OKTPvvYzwEHP4DqLpbPgsrgXGjlih2_H9ptRq3TEMm6rX9YdLnLp96V2GsVssIPX1a5i8Em1RwVOJqapUOOW-z80JOqIY5BP9xvb8ezHS"
                            },
                            {
                                tag: "Educational Forecast",
                                title: "Mastering React in 10 Minutes: Virality Loop",
                                stats: "12.5% CTR Predicted",
                                image: "https://lh3.googleusercontent.com/aida-public/AB6AXuAZABmTZ7QqYy5UKYutC9fFndA3W6nhDO_cn98f1zaP8bRAfqiA6b9IQ0OV2fx2rfr4EmO-oARP1O28ZUhkEIJSuw0c0VtR1HSNe_NfSmQgjTEg5Eads169WDxgESRXS0UFx4o2OkSQPuUDIO-WwniCYK3QL8ZzYUokkWIGEUmJ_Do7Gf2v09quTP7T2rz4RUaNc8uTLSQ2GkN3vXdEZG4FXqQtDsWzkKQNylrbTdAAAN6Fmq_5WYy1YTQjnirjbXiAaY1fWgET874q"
                            }
                        ].map((item, i) => (
                            <motion.article
                                key={item.title}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.2 * i }}
                                className="grid grid-cols-5 gap-8 group cursor-pointer"
                            >
                                <div className="col-span-2 aspect-[3/4] overflow-hidden border border-border-soft">
                                    <img src={item.image} alt={item.title} className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-700" />
                                </div>
                                <div className="col-span-3 flex flex-col justify-center">
                                    <p className="text-[9px] uppercase tracking-widest font-black text-secondary mb-4">{item.tag}</p>
                                    <h4 className="serif-display text-2xl font-bold mb-4 leading-tight group-hover:text-primary transition-colors">{item.title}</h4>
                                    <div className="flex items-center gap-2 text-[9px] font-black text-muted-gray uppercase tracking-widest">
                                        <TrendingUp size={12} className="text-primary" />
                                        <span>{item.stats}</span>
                                    </div>
                                </div>
                            </motion.article>
                        ))}
                    </div>
                </div>
            </section>
        </div>
    );
};

export default PredictiveIntelligence;
