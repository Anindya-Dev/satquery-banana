import React, { useState } from 'react';
import { Search, Upload, Sparkles, Sliders, Image as ImageIcon, Zap, AlertTriangle, ArrowRight, ShieldCheck } from 'lucide-react';

export default function HeroQueryCenter({ 
  currentTask, 
  onSelectTask, 
  queryText, 
  setQueryText, 
  onRunAnalysis, 
  isAnalyzing,
  activeScenario,
  analysisArea,
  setAnalysisArea,
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
        <h2 className="heading-font text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
          Grounding AI Reasoning in <span className="text-orange-600">Satellite Physics</span>
        </h2>
        <p className="mt-2 text-sm sm:text-base text-slate-600">
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
                  ? 'bg-orange-600 text-white border border-orange-700 shadow-md shadow-orange-500/20'
                  : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 hover:text-slate-900 shadow-sm'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-500'}`} />
              <span>{mode.label}</span>
              <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase tracking-wider font-mono font-bold ${
                isActive ? 'bg-orange-700 text-orange-100' : 'bg-slate-100 text-slate-500'
              }`}>
                {mode.badge}
              </span>
            </button>
          );
        })}
      </div>

      {/* Main Query & Upload Console */}
      <div className="glass-panel p-5 border border-slate-200 shadow-xl relative overflow-hidden bg-white">
        
        {/* Ambient Top Radiant Line */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-orange-500/50 to-transparent"></div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-center">
          
          {/* Natural Language Query Bar */}
          <div className="lg:col-span-8 flex flex-col gap-3">
            <label className="text-xs font-bold text-slate-800 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Search className="w-3.5 h-3.5 text-orange-600" />
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
                className="w-full bg-slate-50 border border-slate-300 rounded-xl p-3.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all resize-none font-medium"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <input value={analysisArea.bbox} onChange={(event) => setAnalysisArea({ ...analysisArea, bbox: event.target.value })} aria-label="Area of interest bounding box" placeholder="minLon,minLat,maxLon,maxLat" className="sm:col-span-3 bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono text-slate-800 focus:outline-none focus:border-orange-500" />
              <input value={analysisArea.startDate} onChange={(event) => setAnalysisArea({ ...analysisArea, startDate: event.target.value })} aria-label="Start date" placeholder="Start date, ISO-8601" className="bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono text-slate-800 focus:outline-none focus:border-orange-500" />
              <input value={analysisArea.endDate} onChange={(event) => setAnalysisArea({ ...analysisArea, endDate: event.target.value })} aria-label="End date" placeholder="End date, ISO-8601" className="bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono text-slate-800 focus:outline-none focus:border-orange-500" />
              <span className="text-[10px] text-slate-500 font-mono self-center">AOI uses EPSG:4326 lon/lat.</span>
            </div>

            {/* Quick Prompt Suggestions */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] text-slate-600 font-semibold">Try Prompt:</span>
              {SUGGESTED_PROMPTS.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => setQueryText(prompt)}
                  className="text-[11px] bg-slate-100 hover:bg-orange-50 text-slate-700 hover:text-orange-900 px-2.5 py-1 rounded-lg border border-slate-200 hover:border-orange-300 transition-all text-left truncate max-w-[280px] font-medium"
                >
                  "{prompt.slice(0, 36)}..."
                </button>
              ))}
            </div>
          </div>

          {/* Upload Dropzone & Action Button */}
          <div className="lg:col-span-4 flex flex-col gap-3">
            <label className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
              <Upload className="w-3.5 h-3.5 text-orange-600" />
              Input Remote Sensing Imagery
            </label>

            {/* Upload Area */}
            <div 
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); }}
              className={`border-2 border-dashed rounded-xl p-3 text-center transition-all cursor-pointer flex items-center justify-between px-4 ${
                dragOver 
                  ? 'border-orange-500 bg-orange-50' 
                  : 'border-slate-300 bg-slate-50 hover:border-orange-400 hover:bg-orange-50/40'
              }`}
            >
              <div className="flex items-center gap-3 text-left">
                <div className="p-2 rounded-lg bg-orange-100 text-orange-600">
                  <ImageIcon className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-900">
                    {activeScenario?.imageType === 'pair' ? 'Bi-Temporal Pair (T1 + T2)' : activeScenario?.imageType === 'optical_sar' ? 'Optical + SAR Pair' : 'Single Scene raster'}
                  </p>
                  <p className="text-[10px] text-slate-500 font-mono">
                    {activeScenario?.location || 'GeoTIFF / PNG / Sentinel-2'}
                  </p>
                </div>
              </div>
              <span className="text-[11px] text-orange-800 font-bold px-2 py-1 rounded bg-orange-100 border border-orange-200">
                Loaded
              </span>
            </div>

            {/* Run Analysis Button */}
            <button
              onClick={onRunAnalysis}
              disabled={isAnalyzing}
              className="btn-amber-glow w-full justify-center py-3 text-sm font-extrabold tracking-wide uppercase shadow-lg shadow-orange-500/20"
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
