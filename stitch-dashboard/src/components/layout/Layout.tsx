import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import { motion } from 'framer-motion';

const Layout = () => {
    return (
        <div className="min-h-screen flex flex-col bg-offwhite">
            <Navbar />
            <motion.main
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="max-w-[1400px] mx-auto px-8 lg:px-16 py-12 flex-grow w-full"
            >
                <Outlet />
            </motion.main>

            <footer className="border-t-2 border-charcoal mt-24 py-16 px-8 lg:px-16">
                <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row justify-between items-start gap-12">
                    <div className="max-w-md">
                        <div className="flex items-center gap-6 mb-8">
                            <img
                                alt="Profile"
                                className="w-16 h-16 rounded-none border border-charcoal p-1 hover:scale-105 transition-all cursor-pointer"
                                src="/sourav-profile.jpg"
                            />
                            <div>
                                <h5 className="serif-display text-2xl font-bold">Sourav Chandak</h5>
                                <p className="text-[10px] uppercase tracking-[0.2em] font-bold text-secondary">Creator & Analytics Expert</p>
                            </div>
                        </div>
                        <p className="serif-text text-sm italic text-muted-gray leading-relaxed">
                            "Data tells the story behind every view, like, and share. Understanding the numbers means understanding your audience."
                        </p>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-16">
                        <div className="flex flex-col gap-4">
                            <span className="text-[10px] font-black uppercase tracking-[0.3em] mb-2">Navigation</span>
                            <a href="#" className="text-[11px] font-medium hover:text-primary transition-colors">Journal Archives</a>
                            <a href="#" className="text-[11px] font-medium hover:text-primary transition-colors">Studio Settings</a>
                            <a href="#" className="text-[11px] font-medium hover:text-primary transition-colors">Brand Kit</a>
                        </div>
                        <div className="flex flex-col gap-4">
                            <span className="text-[10px] font-black uppercase tracking-[0.3em] mb-2">Legal</span>
                            <a href="#" className="text-[11px] font-medium hover:text-primary transition-colors">Privacy Policy</a>
                            <a href="#" className="text-[11px] font-medium hover:text-primary transition-colors">Editorial Terms</a>
                        </div>
                        <div className="flex flex-col gap-4">
                            <span className="text-[10px] font-black uppercase tracking-[0.3em] mb-2">Connect</span>
                            <div className="flex gap-4">
                                <span className="text-[11px] font-medium hover:text-primary transition-colors cursor-pointer">Instagram</span>
                                <span className="text-[11px] font-medium hover:text-primary transition-colors cursor-pointer">YouTube</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="max-w-[1400px] mx-auto mt-16 pt-8 border-t border-charcoal/10 flex justify-between items-center">
                    <span className="text-[9px] uppercase tracking-[0.4em] font-bold">© 2024 Creator Analytics • Editorial Edition</span>
                    <span className="serif-text italic text-xs">A premium data experience</span>
                </div>
            </footer>
        </div>
    );
};

export default Layout;
