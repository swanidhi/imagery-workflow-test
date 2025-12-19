import React, { useRef, useState, useEffect } from 'react';
import { X, ChevronLeft, ChevronRight, Lock, Unlock } from 'lucide-react';

export default function ComparisonModal({ sourceImages, initialSourceIndex, aiImages, initialAiIndex, onClose }) {
    // Navigation
    const [srcIndex, setSrcIndex] = useState(initialSourceIndex);
    const [aiIndex, setAiIndex] = useState(initialAiIndex);

    // States for Source (Left)
    const [srcState, setSrcState] = useState({ scale: 1, x: 0, y: 0 });

    // States for AI (Right)
    const [aiState, setAiState] = useState({ scale: 1, x: 0, y: 0 });

    // Sync Toggle
    const [isSynced, setIsSynced] = useState(false);

    // Interaction tracking
    const [draggingPane, setDraggingPane] = useState(null); // 'src' or 'ai'
    const dragStart = useRef({ x: 0, y: 0 });

    useEffect(() => {
        const handleKey = (e) => {
            if (e.key === 'Escape') onClose();
            if (e.key === 'ArrowRight') nextAi();
            if (e.key === 'ArrowLeft') prevAi();
        };
        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
    }, [onClose, aiImages]);

    // Source Nav
    const nextSrc = () => setSrcIndex(prev => (prev + 1) % sourceImages.length);
    const prevSrc = () => setSrcIndex(prev => (prev - 1 + sourceImages.length) % sourceImages.length);

    // AI Nav
    const nextAi = () => setAiIndex(prev => (prev + 1) % aiImages.length);
    const prevAi = () => setAiIndex(prev => (prev - 1 + aiImages.length) % aiImages.length);

    // Generic Handlers
    const handleWheel = (e, pane) => {
        const delta = e.deltaY * -0.001;

        const updateState = (prev) => {
            const newScale = Math.min(Math.max(0.5, prev.scale + delta), 5);
            return { ...prev, scale: newScale };
        };

        if (isSynced) {
            setSrcState(prev => updateState(prev));
            setAiState(prev => updateState(prev));
        } else {
            if (pane === 'src') setSrcState(prev => updateState(prev));
            else setAiState(prev => updateState(prev));
        }
    };

    const handleMouseDown = (e, pane) => {
        setDraggingPane(pane);
        const currentState = pane === 'src' ? srcState : aiState;
        dragStart.current = { x: e.clientX - currentState.x, y: e.clientY - currentState.y };
    };

    const handleMouseMove = (e) => {
        if (!draggingPane) return;
        e.preventDefault();

        const newX = e.clientX - dragStart.current.x;
        const newY = e.clientY - dragStart.current.y;

        const update = { x: newX, y: newY };

        if (isSynced) {
            setSrcState(prev => ({ ...prev, ...update }));
            setAiState(prev => ({ ...prev, ...update }));
        } else {
            if (draggingPane === 'src') setSrcState(prev => ({ ...prev, ...update }));
            else setAiState(prev => ({ ...prev, ...update }));
        }
    };

    const handleMouseUp = () => setDraggingPane(null);

    const getStyle = (s) => ({
        transform: `translate(${s.x}px, ${s.y}px) scale(${s.scale})`,
        cursor: 'grab',
        transition: draggingPane ? 'none' : 'transform 0.1s ease-out'
    });

    const currentAiImg = aiImages[aiIndex];
    const currentSrcUrl = sourceImages[srcIndex];

    return (
        <div className="fixed inset-0 z-[1000] bg-black/95 flex flex-col"
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}>

            {/* Header */}
            <div className="flex justify-between items-center p-4 bg-black/50 backdrop-blur text-white border-b border-border z-50">
                <div className="flex items-center gap-4">
                    <div className="font-semibold">Comparison Mode</div>
                    <button
                        onClick={() => setIsSynced(!isSynced)}
                        className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border transition-colors ${isSynced ? 'bg-primary border-primary text-white' : 'bg-surface border-border text-text-muted hover:text-white'}`}
                    >
                        {isSynced ? <Lock size={12} /> : <Unlock size={12} />}
                        {isSynced ? 'Synced' : 'Independent'}
                    </button>
                </div>
                <button onClick={onClose} className="p-1 hover:bg-white/10 rounded">
                    <X size={20} />
                </button>
            </div>

            {/* Body */}
            <div className="flex-1 flex overflow-hidden">

                {/* LEFT PANE (Source) */}
                <div className="flex-1 border-r border-border/50 relative overflow-hidden flex items-center justify-center bg-black/20"
                    onWheel={(e) => handleWheel(e, 'src')}
                    onMouseDown={(e) => handleMouseDown(e, 'src')}>

                    <div className="absolute top-4 left-4 flex items-center gap-2 z-10">
                        <span className="bg-black/70 px-3 py-1 text-xs rounded-full text-white pointer-events-none">
                            Source ({srcIndex + 1}/{sourceImages.length})
                        </span>
                    </div>

                    {/* Source Navigation Arrows */}
                    {sourceImages.length > 1 && (
                        <>
                            <button onClick={(e) => { e.stopPropagation(); prevSrc(); }}
                                className="absolute left-2 top-1/2 -translate-y-1/2 p-2 bg-black/50 hover:bg-black/80 text-white rounded-full z-20">
                                <ChevronLeft size={24} />
                            </button>
                            <button onClick={(e) => { e.stopPropagation(); nextSrc(); }}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-black/50 hover:bg-black/80 text-white rounded-full z-20">
                                <ChevronRight size={24} />
                            </button>
                        </>
                    )}

                    <img
                        src={`${currentSrcUrl}?wid=1600&hei=1600`}
                        draggable={false}
                        style={getStyle(srcState)}
                        className="max-h-full max-w-full object-contain"
                    />
                </div>

                {/* RIGHT PANE (AI) */}
                <div className="flex-1 relative overflow-hidden flex items-center justify-center bg-black/20"
                    onWheel={(e) => handleWheel(e, 'ai')}
                    onMouseDown={(e) => handleMouseDown(e, 'ai')}>

                    <div className="absolute top-4 left-4 flex items-center gap-2 z-10">
                        <span className="bg-black/70 px-3 py-1 text-xs rounded-full text-white pointer-events-none">
                            Generated ({aiIndex + 1}/{aiImages.length})
                        </span>
                        <span className={`px-2 py-1 text-[10px] rounded uppercase font-bold text-white pointer-events-none ${currentAiImg?.engine_version === 'v2_nanobananapro'
                                ? 'bg-purple-600'
                                : 'bg-blue-600'
                            }`}>
                            {currentAiImg?.engine_version === 'v2_nanobananapro' ? 'V2' : 'V1'}
                        </span>
                        <span className="bg-primary/80 px-2 py-1 text-[10px] rounded uppercase font-bold text-white pointer-events-none">
                            {currentAiImg?.model_id?.split('-').pop()}
                        </span>
                    </div>

                    {/* AI Navigation Arrows */}
                    {aiImages.length > 1 && (
                        <>
                            <button onClick={(e) => { e.stopPropagation(); prevAi(); }}
                                className="absolute left-2 top-1/2 -translate-y-1/2 p-2 bg-black/50 hover:bg-black/80 text-white rounded-full z-20">
                                <ChevronLeft size={24} />
                            </button>
                            <button onClick={(e) => { e.stopPropagation(); nextAi(); }}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-black/50 hover:bg-black/80 text-white rounded-full z-20">
                                <ChevronRight size={24} />
                            </button>
                        </>
                    )}

                    <img
                        src={`http://localhost:8080/output/${currentAiImg?.path}`}
                        draggable={false}
                        style={getStyle(aiState)}
                        className="max-h-full max-w-full object-contain"
                    />
                </div>
            </div>

            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 bg-black/80 px-4 py-2 rounded-full text-xs text-text-muted pointer-events-none backdrop-blur-md border border-white/10">
                Scroll to Zoom • Drag to Pan independently • Use Arrows to Switch Images
            </div>
        </div>
    );
}
