import React, { useState } from 'react';
import { Search, Upload, Sparkles, Sliders, Image as ImageIcon, Zap, AlertTriangle, ArrowRight, ShieldCheck } from 'lucide-react';

export default function HeroQueryCenter({ 
  currentTask, 
  onSelectTask, 
  queryText, 
  setQueryText, 
  onRunAnalysis, 
  isAnalyzing,
  activeScenario
}) {
  const [dragOver, setDragOver] = useState(false);

  const TASK_MODES = [
    { id: "SINGLE_IMAGE_VQA", label: "Single Image VQA", icon: ImageIcon, badge: "VQA" },
    { id: "VISUAL_GROUNDING", label: "Visual Grounding", icon: Sliders, badge: "SAM Mask" },
    { id: "CHANGE_DETECTION", label: "Bi-Temporal Change", icon: Zap, badge: "Mandatory" },
    { id: "OPTICAL_SAR_FUSION", label: "Optical + SAR Fusion", icon: Sparkles, badge: "Cross-Modal" },
    { id: "AGENTIC_ROUTING", label: "Auto Task Router", icon: ShieldCheck, badge: "Agentic" },
  ];

  const SUGGESTED_PROMPTS = [
    "Describe the land-cover composition and major visible geographic features.",
    "Highlight the primary water body referred to in the query.",
    "What changed between these two dates, and where did the change occur?",
    "Use optical and SAR images together to identify built-up and water regions."
  ];

  return (
    <section className="relative px-6 pt-6 pb-4 max-w-7xl mx-auto">
      
      {/* Title & Headline */}
      <div className="mb-6 text-center max-w-3xl mx-auto">
        <h2 className="heading-font text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
          Grounding AI Reasoning in <span className="text-amber-glow">Satellite Physics</span>
        </h2>
        <p className="mt-2 text-sm sm:text-base text-slate-400">
          Execute natural language queries over single rasters, bi-temporal pairs, and cross-modal optical+SAR satellite imagery backed by zero coordinate hallucinations.
        </p>
      </div>

      {/* Task Mode Selector Tabs */}
      <div className="flex flex-wrap items-center justify-center gap-2 mb-6">
        {TASK_MODES.map((mode) => {
          const Icon = mode.icon;
          const isActive = currentTask === mode.id;
          return (
            <button
              key={mode.id}
              onClick={() => onSelectTask(mode.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-200 ${
                isActive
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-lg shadow-amber-500/10'
                  : 'bg-white/5 text-slate-400 border border-white/10 hover:bg-white/10 hover:text-slate-200'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-amber-400' : 'text-slate-500'}`} />
              <span>{mode.label}</span>
              <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase tracking-wider ${
                isActive ? 'bg-amber-500/30 text-amber-200' : 'bg-white/5 text-slate-500'
              }`}>
                {mode.badge}
              </span>
            </button>
          );
        })}
      </div>

      {/* Main Query & Upload Console */}
      <div className="glass-panel p-5 border border-white/10 shadow-2xl relative overflow-hidden">
        
        {/* Ambient Top Radiant Line */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-amber-500/50 to-transparent"></div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-center">
          
          {/* Natural Language Query Bar */}
          <div className="lg:col-span-8 flex flex-col gap-3">
            <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Search className="w-3.5 h-3.5 text-amber-400" />
                Natural Language Query
              </span>
              <span className="text-[11px] text-slate-500 font-mono">Deterministic Interpreter Ready</span>
            </label>
            
            <div className="relative">
              <textarea
                rows={2}
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                placeholder="Ask about land cover, water segmentation, bi-temporal changes, or optical+SAR features..."
                className="w-full bg-slate-950/80 border border-white/10 rounded-xl p-3.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500/50 focus:ring-2 focus:ring-amber-500/20 transition-all resize-none"
              />
            </div>

            {/* Quick Prompt Suggestions */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] text-slate-500 font-medium">Try Prompt:</span>
              {SUGGESTED_PROMPTS.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => setQueryText(prompt)}
                  className="text-[11px] bg-white/5 hover:bg-white/10 text-slate-300 px-2.5 py-1 rounded-lg border border-white/5 transition-all text-left truncate max-w-[280px]"
                >
                  "{prompt.slice(0, 36)}..."
                </button>
              ))}
            </div>
          </div>

          {/* Upload Dropzone & Action Button */}
          <div className="lg:col-span-4 flex flex-col gap-3">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <Upload className="w-3.5 h-3.5 text-amber-400" />
              Input Remote Sensing Imagery
            </label>

            {/* Upload Area */}
            <div 
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); }}
              className={`border-2 border-dashed rounded-xl p-3 text-center transition-all cursor-pointer flex items-center justify-between px-4 ${
                dragOver 
                  ? 'border-amber-500 bg-amber-500/10' 
                  : 'border-white/10 bg-slate-950/40 hover:border-amber-500/30 hover:bg-slate-900/40'
              }`}
            >
              <div className="flex items-center gap-3 text-left">
                <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
                  <ImageIcon className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-200">
                    {activeScenario?.imageType === 'pair' ? 'Bi-Temporal Pair (T1 + T2)' : activeScenario?.imageType === 'optical_sar' ? 'Optical + SAR Pair' : 'Single Scene raster'}
                  </p>
                  <p className="text-[10px] text-slate-400 font-mono">
                    {activeScenario?.location || 'GeoTIFF / PNG / Sentinel-2'}
                  </p>
                </div>
              </div>
              <span className="text-[11px] text-amber-400 font-medium px-2 py-1 rounded bg-amber-500/10 border border-amber-500/20">
                Loaded
              </span>
            </div>

            {/* Run Analysis Button */}
            <button
              onClick={onRunAnalysis}
              disabled={isAnalyzing}
              className="btn-primary w-full justify-center py-3 text-sm font-bold tracking-wide uppercase shadow-lg shadow-amber-500/20"
            >
              {isAnalyzing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Executing Pipeline...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Run Grounded Analysis</span>
                  <ArrowRight className="w-4 h-4 ml-1" />
                </>
              )}
            </button>
          </div>

        </div>
      </div>
    </section>
  );
}
