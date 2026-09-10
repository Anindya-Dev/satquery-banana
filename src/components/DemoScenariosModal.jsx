import React from 'react';
import { X, Sparkles, CheckCircle2, Play, Layers, Zap, Sliders, ShieldCheck } from 'lucide-react';
import { DEMO_SCENARIOS } from '../data/demoScenarios';

export default function DemoScenariosModal({ isOpen, onClose, onSelectScenario, activeScenarioId }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="glass-panel w-full max-w-4xl max-h-[85vh] flex flex-col border border-white/15 shadow-2xl overflow-hidden relative">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between p-5 border-b border-white/10 bg-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="heading-font text-lg font-bold text-white flex items-center gap-2">
                <span>SIH Evaluator Demo Scenarios</span>
                <span className="badge-tag bg-amber-500/20 text-amber-300 border border-amber-500/30">Official Suite</span>
              </h3>
              <p className="text-xs text-slate-400">Select any pre-loaded scenario to demonstrate SatQuery AI capabilities</p>
            </div>
          </div>

          <button 
            onClick={onClose}
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all border border-white/5"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body: Scenarios List */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {DEMO_SCENARIOS.map((scen, idx) => {
            const isSelected = scen.id === activeScenarioId;

            return (
              <div 
                key={scen.id}
                onClick={() => {
                  onSelectScenario(scen);
                  onClose();
                }}
                className={`p-4 rounded-xl border transition-all cursor-pointer group flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
                  isSelected 
                    ? 'bg-amber-500/25 border-amber-400 shadow-xl shadow-amber-500/20 ring-1 ring-amber-400/40' 
                    : 'bg-slate-900/90 border-white/15 hover:border-amber-400/50 hover:bg-slate-800/90'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-mono font-bold text-sm shrink-0 ${
                    isSelected ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/40' : 'bg-white/10 text-slate-300 group-hover:text-amber-400 group-hover:bg-white/15'
                  }`}>
                    0{idx + 1}
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <h4 className={`text-sm font-bold transition-colors ${isSelected ? 'text-amber-200 font-extrabold' : 'text-white group-hover:text-amber-300'}`}>
                        {scen.title}
                      </h4>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                        isSelected 
                          ? 'bg-amber-500/30 text-amber-200 border-amber-400/40' 
                          : 'bg-white/10 text-slate-200 border-white/15'
                      }`}>
                        {scen.badge}
                      </span>
                    </div>

                    <p className={`text-xs mb-2 font-mono leading-relaxed ${isSelected ? 'text-amber-100 font-semibold' : 'text-slate-300'}`}>
                      "{scen.query}"
                    </p>

                    <div className="flex items-center gap-4 text-[11px] text-slate-400 font-mono">
                      <span>Location: <strong className="text-white font-semibold">{scen.location}</strong></span>
                      <span>Date: <strong className="text-white font-semibold">{scen.date}</strong></span>
                    </div>
                  </div>
                </div>

                {/* Select Button */}
                <button className={`btn-primary py-2 px-4 text-xs font-bold shrink-0 ${isSelected ? 'opacity-100 bg-amber-500 text-slate-950 hover:bg-amber-400' : 'opacity-90 group-hover:opacity-100'}`}>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>{isSelected ? 'Loaded' : 'Load Demo'}</span>
                </button>
              </div>
            );
          })}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-white/10 bg-slate-950/60 text-xs text-slate-400 flex items-center justify-between font-mono">
          <span>All scenarios pre-verified with deterministic ground truth</span>
          <button 
            onClick={onClose}
            className="btn-secondary py-1.5 px-3 text-xs"
          >
            Close Window
          </button>
        </div>

      </div>
    </div>
  );
}
