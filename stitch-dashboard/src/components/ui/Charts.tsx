import React from 'react';
import {
    AreaChart, Area, BarChart, Bar, LineChart, Line,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend, Brush, ReferenceLine
} from 'recharts';
import { motion } from 'framer-motion';

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-charcoal text-white p-3 border border-charcoal shadow-lg">
                <p className="text-[10px] uppercase tracking-widest font-bold mb-1">{label}</p>
                {payload.map((entry: any, index: number) => (
                    <p key={index} className="text-sm font-medium" style={{ color: entry.color }}>
                        {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
                    </p>
                ))}
            </div>
        );
    }
    return null;
};

// Formatting helpers
const formatMillions = (value: number | string | undefined) => {
    if (typeof value === 'number') return `${(value / 1000000).toFixed(1)}M`;
    return '';
};

const formatThousands = (value: number | string | undefined) => {
    if (typeof value === 'number') return `${(value / 1000).toFixed(0)}K`;
    return '';
};

const formatPercent = (value: number | string | undefined) => {
    if (typeof value === 'number') return `${value}%`;
    return '';
};

const formatValue = (value: number | string | undefined) => {
    if (typeof value === 'number') return value.toString();
    return value ? value.toString() : '';
};

// Animated Growth Chart
interface GrowthChartProps {
    data: { name: string; value: number }[];
    color?: string;
}

export const GrowthChart: React.FC<GrowthChartProps> = ({ data, color = "#2d6a6d" }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="w-full h-full"
        >
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                        <linearGradient id="colorGrowth" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={color} stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" vertical={false} />
                    <XAxis
                        dataKey="name"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 10, fill: '#666', fontWeight: 600 }}
                    />
                    <YAxis
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 10, fill: '#666' }}
                        tickFormatter={formatMillions}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Area
                        type="monotone"
                        dataKey="value"
                        stroke={color}
                        strokeWidth={3}
                        fill="url(#colorGrowth)"
                        animationDuration={2000}
                        name="Subscribers"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </motion.div>
    );
};

// Engagement Bar Chart
interface EngagementBarChartProps {
    data: { name: string; engagement: number; views: number }[];
}

export const EngagementBarChart: React.FC<EngagementBarChartProps> = ({ data }) => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="w-full h-full"
        >
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" vertical={false} />
                    <XAxis
                        dataKey="name"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 9, fill: '#666', fontWeight: 600 }}
                        interval={0}
                        angle={-45}
                        textAnchor="end"
                        height={60}
                    />
                    <YAxis
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 10, fill: '#666' }}
                        tickFormatter={formatPercent}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar
                        dataKey="engagement"
                        fill="#2d6a6d"
                        radius={[4, 4, 0, 0]}
                        animationDuration={1500}
                        name="Engagement %"
                    />
                </BarChart>
            </ResponsiveContainer>
        </motion.div>
    );
};

// Sentiment Pie Chart
interface SentimentPieChartProps {
    data: { name: string; value: number; color: string }[];
}

export const SentimentPieChart: React.FC<SentimentPieChartProps> = ({ data }) => {
    return (
        <motion.div
            initial={{ opacity: 0, rotate: -180 }}
            animate={{ opacity: 1, rotate: 0 }}
            transition={{ duration: 1, type: 'spring' }}
            className="w-full h-full"
        >
            <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                        animationDuration={1500}
                        animationBegin={300}
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                    <Legend
                        verticalAlign="bottom"
                        height={36}
                        formatter={(value) => <span className="text-[10px] uppercase tracking-widest font-bold">{value}</span>}
                    />
                </PieChart>
            </ResponsiveContainer>
        </motion.div>
    );
};

// Performance Line Chart
interface PerformanceChartProps {
    data: { name: string; views: number; engagement: number }[];
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({ data }) => {
    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="w-full h-full"
        >
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                    <XAxis
                        dataKey="name"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 10, fill: '#666', fontWeight: 600 }}
                    />
                    <YAxis
                        yAxisId="left"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 10, fill: '#2d6a6d' }}
                        tickFormatter={formatThousands}
                    />
                    <YAxis
                        yAxisId="right"
                        orientation="right"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 10, fill: '#c06c52' }}
                        tickFormatter={formatPercent}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend
                        verticalAlign="top"
                        height={36}
                        formatter={(value) => <span className="text-[10px] uppercase tracking-widest font-bold">{value}</span>}
                    />
                    <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="views"
                        stroke="#2d6a6d"
                        strokeWidth={2}
                        dot={{ fill: '#2d6a6d', strokeWidth: 2, r: 4 }}
                        activeDot={{ r: 6, fill: '#2d6a6d' }}
                        animationDuration={2000}
                        name="Views"
                    />
                    <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="engagement"
                        stroke="#c06c52"
                        strokeWidth={2}
                        name="Engagement %"
                    />
                    <ReferenceLine y={0} stroke="#000" />
                    <Brush
                        dataKey="name"
                        height={30}
                        stroke="#2d6a6d"
                        fill="#f7f7f7"
                        tickFormatter={() => ""}
                    />
                </LineChart>
            </ResponsiveContainer>
        </motion.div>
    );
};

// Stats Counter with Animation
interface AnimatedCounterProps {
    value: number;
    suffix?: string;
    prefix?: string;
    decimals?: number;
}

export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
    value,
    suffix = '',
    prefix = '',
    decimals = 0
}) => {
    const [count, setCount] = React.useState(0);

    React.useEffect(() => {
        let start = 0;
        const duration = 2000;
        const increment = value / (duration / 16);

        const timer = setInterval(() => {
            start += increment;
            if (start >= value) {
                setCount(value);
                clearInterval(timer);
            } else {
                setCount(start);
            }
        }, 16);

        return () => clearInterval(timer);
    }, [value]);

    return (
        <span>
            {prefix}{count.toFixed(decimals)}{suffix}
        </span>
    );
};
