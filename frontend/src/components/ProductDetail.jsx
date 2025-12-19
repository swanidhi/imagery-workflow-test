import React, { useState, useEffect } from 'react';
import { Sparkles, ArrowRightLeft } from 'lucide-react';

export default function ProductDetail({ data, onGenerate, onCompare }) {
    // Now managing a LIST of selected sources
    const [selectedSources, setSelectedSources] = useState([]);

    // Keep track of "Active" index for comparison modal entry/navigation
    const [lastClickedIndex, setLastClickedIndex] = useState(0);

    const [activeGenIndex, setActiveGenIndex] = useState(0);
    const [generating, setGenerating] = useState(false);

    // Auto-select first source by default
    useEffect(() => {
        if (data.ghost_images?.length) {
            setSelectedSources([data.ghost_images[0]]);
            setLastClickedIndex(0);
        } else {
            setSelectedSources([]);
            setLastClickedIndex(0);
        }
        setActiveGenIndex(0);
    }, [data]);

    const activeGen = data.generated_images?.[activeGenIndex];

    const handleGenerateClick = async () => {
        setGenerating(true);
        // Pass the LIST of selected source image URLs
        await onGenerate(selectedSources);
        setGenerating(false);
    };

    const handleSourceClick = (url, index, e) => {
        // Check for modifier key (Cmd/Ctrl/Shift)
        const isMultiSelect = e.metaKey || e.ctrlKey || e.shiftKey;

        if (isMultiSelect) {
            // Toggle logic
            if (selectedSources.includes(url)) {
                // Remove if already selected (but prevent empty list? maybe not)
                const newList = selectedSources.filter(s => s !== url);
                setSelectedSources(newList);
            } else {
                // Add
                setSelectedSources([...selectedSources, url]);
            }
        } else {
            // Exclusive select
            setSelectedSources([url]);
        }

        // Always update last clicked for comparison context
        setLastClickedIndex(index);
    };

    // Format specs
    const specs = Object.entries(data.specifications || {}).map(([k, v]) => (
        <div key={k} className="flex flex-col">
            <span className="text-[10px] text-text-muted uppercase tracking-wider">{k}</span>
            <span className="text-xs font-medium">{v}</span>
        </div>
    ));

    const hasSelection = selectedSources.length > 0;

    return (
        <div className="flex-1 flex flex-col h-full bg-background">
            {/* Top Bar */}
            <div className="h-[60px] border-b border-border flex items-center justify-between px-6 bg-surface flex-shrink-0">
                <h2 className="text-sm font-semibold truncate max-w-xl" title={data.product_name}>{data.product_name}</h2>
                <div className="flex gap-2">
                    <button
                        onClick={() => onCompare(lastClickedIndex, activeGenIndex)}
                        disabled={!hasSelection || !activeGen}
                        className="flex items-center gap-2 px-3 py-1.5 rounded bg-surface border border-border hover:bg-surface-highlight disabled:opacity-50 text-xs font-medium transition-colors"
                    >
                        <ArrowRightLeft size={14} /> Compare
                    </button>
                    <button
                        onClick={handleGenerateClick}
                        disabled={generating}
                        className="flex items-center gap-2 px-3 py-1.5 rounded bg-primary hover:bg-primary-hover text-white disabled:opacity-70 text-xs font-medium transition-colors"
                    >
                        {generating ? (
                            <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : <Sparkles size={14} />}
                        Generate ({selectedSources.length})
                    </button>
                </div>
            </div>

            <div className="flex-1 flex overflow-hidden">
                {/* Source Column */}
                <div className="flex-1 flex flex-col border-r border-border p-6 overflow-y-auto">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2 text-xs font-bold text-text-muted uppercase tracking-wider">
                            <div className="w-1 h-3 bg-warning rounded-full" /> Source Ghost Images
                        </div>
                        <span className="text-[10px] text-text-muted">
                            {selectedSources.length} selected (Cmd+Click)
                        </span>
                    </div>

                    <div className="grid grid-cols-3 gap-3 mb-6">
                        {data.ghost_images?.map((url, i) => {
                            const isSelected = selectedSources.includes(url);
                            return (
                                <div
                                    key={url}
                                    onClick={(e) => handleSourceClick(url, i, e)}
                                    className={`aspect-square border rounded-lg overflow-hidden cursor-pointer transition-all hover:border-primary bg-black/20 ${isSelected ? 'ring-2 ring-primary border-transparent shadow-lg shadow-primary/10' : 'border-border'}`}
                                >
                                    <img src={`${url}?wid=200&hei=200`} className="w-full h-full object-contain p-2" />
                                    {isSelected && (
                                        <div className="absolute top-1 right-1 w-4 h-4 bg-primary text-white rounded-full flex items-center justify-center text-[10px] font-bold">
                                            ✓
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>

                    <div className="bg-surface rounded-lg p-4 border border-border">
                        <h3 className="text-xs font-bold mb-3">Product Data</h3>
                        <div className="space-y-3">
                            <div className="flex flex-col">
                                <span className="text-[10px] text-text-muted uppercase">Brand</span>
                                <span className="text-sm font-medium">{data.brand}</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-[10px] text-text-muted uppercase">Class</span>
                                <span className="text-sm font-medium">{data.class_description}</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-[10px] text-text-muted uppercase">Tranche</span>
                                <span className="text-sm font-medium">{data.tranche}</span>
                            </div>
                            <div className="h-px bg-border my-2" />
                            <div className="grid grid-cols-2 gap-3">
                                {specs}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Generated Column */}
                <div className="flex-1 flex flex-col p-6 overflow-y-auto">
                    <div className="flex items-center gap-2 mb-4 text-xs font-bold text-text-muted uppercase tracking-wider">
                        <div className="w-1 h-3 bg-success rounded-full" /> AI Generated
                    </div>

                    <div className="grid grid-cols-3 gap-3 mb-6">
                        {data.generated_images?.map((img, i) => (
                            <div
                                key={i}
                                onClick={() => setActiveGenIndex(i)}
                                className={`aspect-square border rounded-lg overflow-hidden cursor-pointer bg-surface relative ${i === activeGenIndex ? 'ring-2 ring-success border-transparent shadow-lg shadow-success/10' : 'border-border'}`}
                            >
                                <img src={`http://localhost:8080/output/${img.path}`} className="w-full h-full object-cover" />
                                <div className="absolute bottom-1 left-1 px-1.5 py-0.5 bg-black/60 text-white text-[9px] font-bold rounded backdrop-blur-sm truncate max-w-[90%]">
                                    {img.model_id}
                                </div>
                            </div>
                        ))}
                    </div>

                    {activeGen && (
                        <div className="bg-surface rounded-lg p-4 border border-border flex-1 border-l-4 border-l-primary/50">
                            <h3 className="text-xs font-bold mb-2 text-text-muted uppercase">Prompts</h3>
                            <div className="space-y-4">
                                <div>
                                    <span className="text-[10px] text-success font-bold uppercase block mb-1">Active Prompt</span>
                                    <p className="text-xs font-mono bg-black/30 p-2 rounded text-text-muted leading-relaxed whitespace-pre-wrap">
                                        {activeGen.prompts.positive}
                                    </p>
                                </div>
                                {activeGen.prompts.negative && (
                                    <div>
                                        <span className="text-[10px] text-danger font-bold uppercase block mb-1">Negative Prompt</span>
                                        <p className="text-xs font-mono bg-black/30 p-2 rounded text-text-muted leading-relaxed">
                                            {activeGen.prompts.negative}
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
