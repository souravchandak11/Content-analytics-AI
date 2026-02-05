import React from 'react';
import { motion } from 'framer-motion';
import { ArrowUpRight, ArrowDownRight, Check, TrendingUp } from 'lucide-react';

interface MetricCardProps {
    label: string;
    value: string;
    delta?: string;
    deltaType?: 'positive' | 'negative' | 'neutral' | 'trend';
    description: string;
    index: number;
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, delta, deltaType, description, index }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 * index }}
            className="border-t border-charcoal pt-6 group hover:bg-offwhite/50 transition-colors duration-300"
        >
            <span className="text-[10px] font-bold uppercase tracking-[0.3em] text-secondary block mb-6">{label}</span>
            <div className="flex flex-col">
                <span className="serif-display text-6xl font-black group-hover:text-primary transition-colors">{value}</span>
                {delta && (
                    <div className="flex items-center gap-2 mt-2">
                        {deltaType === 'positive' && <ArrowUpRight className="text-primary w-4 h-4" />}
                        {deltaType === 'negative' && <ArrowDownRight className="text-secondary w-4 h-4" />}
                        {deltaType === 'neutral' && <Check className="text-primary w-4 h-4" />}
                        {deltaType === 'trend' && <TrendingUp className="text-primary w-4 h-4" />}
                        <span className={`text-xs font-bold uppercase tracking-widest ${deltaType === 'negative' ? 'text-secondary' : 'text-primary'}`}>
                            {delta}
                        </span>
                    </div>
                )}
            </div>
            <p className="serif-text mt-6 text-charcoal/60 leading-relaxed italic">{description}</p>
        </motion.div>
    );
};

export default MetricCard;
