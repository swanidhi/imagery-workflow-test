import React, { useState, useMemo } from 'react';
import { Search, ChevronLeft, Menu, Sparkles, Filter } from 'lucide-react';

export default function Sidebar({ products, selectedCupid, onSelect, isOpen, setIsOpen }) {
    const [search, setSearch] = useState("");
    const [trancheFilter, setTrancheFilter] = useState("");
    const [classFilter, setClassFilter] = useState("");
    const [generatedOnly, setGeneratedOnly] = useState(false);

    // Extract unique tranches
    const tranches = useMemo(() => {
        return [...new Set(products.map(p => p.tranche))].filter(Boolean).sort();
    }, [products]);

    // Extract unique classes
    const classes = useMemo(() => {
        return [...new Set(products.map(p => p.class_description))].filter(Boolean).sort();
    }, [products]);

    // Filtering
    const filteredProducts = useMemo(() => {
        return products.filter(p => {
            const matchesSearch = !search ||
                p.name.toLowerCase().includes(search.toLowerCase()) ||
                p.cupid_name.toLowerCase().includes(search.toLowerCase());
            const matchesTranche = !trancheFilter || p.tranche === trancheFilter;
            const matchesClass = !classFilter || p.class_description === classFilter;
            const matchesGen = !generatedOnly || p.has_images;
            return matchesSearch && matchesTranche && matchesClass && matchesGen;
        });
    }, [products, search, trancheFilter, classFilter, generatedOnly]);

    if (!isOpen) {
        return (
            <div className="w-[60px] bg-surface border-r border-border flex flex-col items-center py-4 relative z-20">
                <button onClick={() => setIsOpen(true)} className="p-2 hover:bg-surface-highlight rounded-md text-text-muted hover:text-text">
                    <Menu size={24} />
                </button>
                <div className="mt-4 flex flex-col gap-4">
                    <div className="w-8 h-[1px] bg-border" />
                    {generatedOnly && (
                        <div className="w-2 h-2 rounded-full bg-primary" title="Generated Only Active" />
                    )}
                </div>
            </div>
        );
    }

    return (
        <div className="w-[340px] bg-surface border-r border-border flex flex-col relative flex-shrink-0 z-20 transition-all">
            <button
                onClick={() => setIsOpen(false)}
                className="absolute top-4 -right-10 w-8 h-8 flex items-center justify-center bg-surface border border-l-0 border-border rounded-r-md text-text-muted hover:text-text z-50">
                <ChevronLeft size={16} />
            </button>

            <div className="p-4 border-b border-border bg-surface/50 backdrop-blur-sm">
                <h1 className="text-sm font-bold bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent mb-4 tracking-tight">
                    AI Imagery Workbench
                </h1>

                <div className="flex flex-col gap-3">
                    {/* Row 1: Search & Toggle */}
                    <div className="flex gap-2">
                        <div className="relative flex-1 group">
                            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 text-text-muted group-focus-within:text-primary transition-colors" size={14} />
                            <input
                                type="text"
                                placeholder="Search products..."
                                className="w-full bg-background border border-border rounded-lg pl-9 pr-2 py-2 text-xs focus:ring-1 focus:ring-primary focus:border-primary outline-none text-text placeholder-text-muted/70 transition-all shadow-sm"
                                value={search}
                                onChange={e => setSearch(e.target.value)}
                            />
                        </div>
                        <button
                            title="Show Generated Only"
                            className={`px-2.5 rounded-lg border transition-all flex items-center justify-center ${generatedOnly
                                ? "bg-primary border-primary text-white shadow-md shadow-primary/20"
                                : "bg-background border-border text-text-muted hover:text-text hover:border-text-muted"
                                }`}
                            onClick={() => setGeneratedOnly(!generatedOnly)}
                        >
                            <Sparkles size={16} className={generatedOnly ? "fill-white/20" : ""} />
                        </button>
                    </div>

                    {/* Row 2: Filters */}
                    <div className="flex gap-2">
                        <div className="relative flex-1">
                            <select
                                className="w-full appearance-none bg-background border border-border rounded-lg px-2.5 py-1.5 text-xs text-text outline-none focus:ring-1 focus:ring-primary cursor-pointer hover:border-text-muted transition-colors"
                                value={trancheFilter}
                                onChange={e => setTrancheFilter(e.target.value)}
                            >
                                <option value="">All Tranches</option>
                                {tranches.map(t => <option key={t} value={t}>{t}</option>)}
                            </select>
                            <Filter size={10} className="absolute right-2 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none opacity-50" />
                        </div>

                        <div className="relative flex-1">
                            <select
                                className="w-full appearance-none bg-background border border-border rounded-lg px-2.5 py-1.5 text-xs text-text outline-none focus:ring-1 focus:ring-primary cursor-pointer hover:border-text-muted transition-colors"
                                value={classFilter}
                                onChange={e => setClassFilter(e.target.value)}
                            >
                                <option value="">All Classes</option>
                                {classes.map(c => <option key={c} value={c}>{c}</option>)}
                            </select>
                            <ChevronLeft size={10} className="absolute right-2 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none opacity-50 -rotate-90" />
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
                {filteredProducts.slice(0, 500).map(p => (
                    <div
                        key={p.cupid_name}
                        onClick={() => onSelect(p.cupid_name)}
                        className={`group relative p-3 rounded-lg cursor-pointer border transition-all ${selectedCupid === p.cupid_name
                            ? "bg-primary/5 border-primary shadow-sm"
                            : "bg-transparent border-transparent hover:bg-surface-highlight"
                            }`}
                    >
                        <div className="flex justify-between items-center mb-1">
                            <span className={`font-mono text-[10px] ${selectedCupid === p.cupid_name ? "text-primary font-bold" : "text-text-muted group-hover:text-text"}`}>
                                {p.cupid_name}
                            </span>
                            {p.has_images && (
                                <span className="flex items-center gap-1 text-[9px] uppercase font-bold text-primary bg-primary/10 px-1.5 py-0.5 rounded-full">
                                    <Sparkles size={8} /> Gen
                                </span>
                            )}
                        </div>
                        <div className={`text-xs font-medium line-clamp-2 ${selectedCupid === p.cupid_name ? "text-text" : "text-text/80"}`}>
                            {p.name}
                        </div>
                        <div className="text-[10px] text-text-muted mt-1 truncate opacity-70 group-hover:opacity-100 transition-opacity">
                            {p.class_description}
                        </div>

                        {/* Active Indicator */}
                        {selectedCupid === p.cupid_name && (
                            <div className="absolute left-0 top-3 bottom-3 w-[3px] bg-primary rounded-r-full" />
                        )}
                    </div>
                ))}

                {filteredProducts.length === 0 && (
                    <div className="text-center py-8 text-text-muted flex flex-col items-center gap-2">
                        <Search size={24} className="opacity-20" />
                        <span className="text-xs">No products found</span>
                    </div>
                )}

                {filteredProducts.length > 500 && (
                    <div className="text-center text-[10px] text-text-muted py-4 uppercase tracking-wider">
                        • {filteredProducts.length - 500} more products •
                    </div>
                )}
            </div>
        </div>
    );
}
