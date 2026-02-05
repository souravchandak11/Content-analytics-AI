import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Search, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const location = useLocation();

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const navLinks = [
        { name: 'Overview', path: '/' },
        { name: 'YouTube', path: '/youtube' },
        { name: 'Instagram', path: '/instagram' },
        { name: 'Predictions', path: '/predictions' },
        { name: 'Sentiment', path: '/sentiment' },
    ];

    return (
        <nav className={`sticky top-0 z-50 transition-all duration-300 ${scrolled ? 'bg-offwhite/90 backdrop-blur-md border-b border-border-soft py-4' : 'bg-offwhite border-b border-border-soft py-6'}`}>
            <div className="max-w-[1400px] mx-auto px-8 lg:px-16 flex items-center justify-between">
                <div className="flex items-center gap-12">
                    <Link to="/" className="flex flex-col leading-none group">
                        <span className="serif-display text-2xl font-black tracking-tighter uppercase italic group-hover:text-primary transition-colors">The Creator</span>
                        <span className="text-[9px] uppercase tracking-[0.4em] font-semibold text-secondary">Quarterly Analytics</span>
                    </Link>

                    <div className="hidden lg:flex items-center gap-8 text-[10px] uppercase tracking-[0.25em] font-medium text-charcoal/60">
                        {navLinks.map((link) => (
                            <Link
                                key={link.name}
                                to={link.path}
                                className={`nav-link transition-colors hover:text-primary ${location.pathname === link.path ? 'text-charcoal border-b-2 border-primary' : ''}`}
                            >
                                {link.name}
                            </Link>
                        ))}
                    </div>
                </div>

                <div className="flex items-center gap-8">
                    <div className="hidden sm:flex flex-col items-end">
                        <span className="text-[10px] uppercase tracking-widest font-bold">Vol. 24 • No. 08</span>
                        <span className="text-[9px] text-muted-gray uppercase italic">Last 30 Days Portfolio</span>
                    </div>

                    <div className="flex items-center gap-5 border-l border-charcoal/10 pl-8">
                        <button onClick={() => setIsOpen(!isOpen)} className="hover:text-primary transition-colors">
                            {isOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                        <div className="w-10 h-10 rounded-full border border-charcoal/20 overflow-hidden cursor-pointer">
                            <img
                                alt="User"
                                className="w-full h-full object-cover"
                                src="https://lh3.googleusercontent.com/aida-public/AB6AXuCxgbEEMm4yJMKWcjIqVVQgkoyewzUqoNVLNUsKIWVRwzxttHQY9NLIxR33sV7UrPpMZRyMDSg8yKRHl1C60Kic-lvA7hZfOQKGK6SZ6Uo8RSUNqHO9aevl1qOENyWjxR5YIByNN77nN29O0pMF1HY_3Y-mbyROrUt2SVa_prXWdQvPZgr9Vq4xbXhuUzNLAHkxQ21xdiiOf_fTolcEI7arG08DQuHjTf6-Z7I4NKTBtSP2mhMLqgDfZt8RLeRMupmmpUr9C1u2PaO-"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="lg:hidden absolute top-full left-0 right-0 bg-offwhite/98 backdrop-blur-lg border-b border-border-soft p-8 z-40"
                    >
                        <div className="flex flex-col gap-6 text-sm uppercase tracking-[0.2em] font-medium">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.name}
                                    to={link.path}
                                    onClick={() => setIsOpen(false)}
                                    className="hover:text-primary transition-colors"
                                >
                                    {link.name}
                                </Link>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
};

export default Navbar;
