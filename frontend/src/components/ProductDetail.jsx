import React, { useState, useEffect } from 'react';
import { Sparkles, ArrowRightLeft } from 'lucide-react';

export default function ProductDetail({ data, onGenerate, onCompare }) {
    // Now managing a LIST of selected sources
    const [selectedSources, setSelectedSources] = useState([]);

    // Keep track of "Active" index for comparison modal entry/navigation
    const [lastClickedIndex, setLastClickedIndex] = useState(0);

    const [activeGenIndex, setActiveGenIndex] = useState(0);
    const [generating, setGenerating] = useState(false);

    // Layout States
    const [isDataExpanded, setIsDataExpanded] = useState(false);
    const [promptTab, setPromptTab] = useState('positive');

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
                <div className="flex-1 flex flex-col border-r border-border overflow-hidden">
                    {/* Top: Images (70% Height) */}
                    <div className="h-[70%] flex flex-col p-6 border-b border-border overflow-y-auto">
                        <div className="flex items-center justify-between mb-4 flex-shrink-0">
                            <div className="flex items-center gap-2 text-xs font-bold text-text-muted uppercase tracking-wider">
                                <div className="w-1 h-3 bg-warning rounded-full" /> Source Ghost Images
                            </div>
                            <span className="text-[10px] text-text-muted">
                                {selectedSources.length} selected (Cmd+Click)
                            </span>
                        </div>

                        <div className="grid grid-cols-3 gap-3">
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
                    </div>

                    {/* Bottom: Product Data (30% Height, Collapsible) */}
                    <div className="flex-1 p-6 overflow-y-auto bg-surface/30">
                        <div className="bg-surface rounded-lg border border-border overflow-hidden">
                            <div
                                className="p-3 flex items-center justify-between cursor-pointer hover:bg-surface-highlight transition-colors"
                                onClick={() => setIsDataExpanded(!isDataExpanded)}
                            >
                                <div className="flex items-center gap-2 overflow-hidden">
                                    <h3 className="text-xs font-bold text-text-muted uppercase flex-shrink-0">Product Data</h3>
                                    {!isDataExpanded && (
                                        <div className="flex items-center gap-2 ml-4">
                                            <span className="text-[10px] bg-black/20 px-2 py-0.5 rounded text-text-muted truncate max-w-[100px]">{data.brand}</span>
                                            <span className="text-[10px] bg-black/20 px-2 py-0.5 rounded text-text-muted truncate max-w-[100px]">{data.class_description}</span>
                                            <span className="text-[10px] bg-black/20 px-2 py-0.5 rounded text-text-muted truncate max-w-[80px]">{data.tranche}</span>
                                        </div>
                                    )}
                                </div>
                                <span className="text-xs text-text-muted">{isDataExpanded ? 'Less' : 'More'}</span>
                            </div>

                            {isDataExpanded && (
                                <div className="p-4 border-t border-border bg-black/20">
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
                            )}
                        </div>
                    </div>
                </div>

                {/* Generated Column */}
                <div className="flex-1 flex flex-col overflow-hidden">
                    {/* Top: Images (70% Height) */}
                    <div className="h-[70%] flex flex-col p-6 border-b border-border overflow-y-auto">
                        <div className="flex items-center gap-2 mb-4 text-xs font-bold text-text-muted uppercase tracking-wider flex-shrink-0">
                            <div className="w-1 h-3 bg-success rounded-full" /> AI Generated
                        </div>

                        <div className="grid grid-cols-3 gap-3">
                            {data.generated_images?.map((img, i) => (
                                <div
                                    key={i}
                                    onClick={() => setActiveGenIndex(i)}
                                    className={`aspect-square border rounded-lg overflow-hidden cursor-pointer bg-surface relative ${i === activeGenIndex ? 'ring-2 ring-success border-transparent shadow-lg shadow-success/10' : 'border-border'}`}
                                >
                                    <img src={`http://localhost:8080/output/${img.path}`} className="w-full h-full object-cover" />
                                    <div className="absolute bottom-1 left-1 flex gap-1">
                                        <span className={`px-1.5 py-0.5 text-[9px] font-bold rounded backdrop-blur-sm ${img.engine_version === 'v2_nanobananapro'
                                            ? 'bg-purple-600/80 text-white'
                                            : 'bg-blue-600/80 text-white'
                                            }`}>
                                            {img.engine_version === 'v2_nanobananapro' ? 'V2' : 'V1'}
                                        </span>
                                        <span className="px-1.5 py-0.5 bg-black/60 text-white text-[9px] font-bold rounded backdrop-blur-sm truncate max-w-[70px]">
                                            {img.model_id?.split('-').pop()}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Bottom: Prompts (30% Height, Tabbed) */}
                    <div className="flex-1 p-6 overflow-y-auto bg-surface/30">
                        {activeGen && (
                            <div className="flex flex-col h-full">
                                <div className="flex items-center gap-4 mb-3 border-b border-border pb-2">
                                    <button
                                        onClick={() => setPromptTab('positive')}
                                        className={`text-xs font-bold uppercase pb-1 transition-colors ${promptTab === 'positive' ? 'text-success border-b-2 border-success' : 'text-text-muted hover:text-white'}`}
                                    >
                                        Positive Prompt
                                    </button>
                                    <button
                                        onClick={() => setPromptTab('negative')}
                                        className={`text-xs font-bold uppercase pb-1 transition-colors ${promptTab === 'negative' ? 'text-danger border-b-2 border-danger' : 'text-text-muted hover:text-white'}`}
                                    >
                                        Negative Prompt
                                    </button>
                                </div>

                                <div className="bg-surface rounded-lg p-3 border border-border flex-1 overflow-y-auto font-mono text-xs text-text-muted bg-black/20 leading-relaxed whitespace-pre-wrap">
                                    {promptTab === 'positive' ? activeGen.prompts.positive : (activeGen.prompts.negative || 'No negative prompt.')}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
