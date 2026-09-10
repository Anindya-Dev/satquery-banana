import React from 'react';
import { X, Sparkles, CheckCircle2, Play, Layers, Zap, Sliders, ShieldCheck } from 'lucide-react';
import { DEMO_SCENARIOS } from '../data/demoScenarios';

export default function DemoScenariosModal({ isOpen, onClose, onSelectScenario, activeScenarioId }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md animate-fadeIn">
      <div className="glass-panel w-full max-w-4xl max-h-[85vh] flex flex-col border border-slate-200 shadow-2xl overflow-hidden relative bg-white">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-orange-100 text-orange-600 border border-orange-200">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="heading-font text-lg font-bold text-slate-900 flex items-center gap-2">
                <span>SIH Evaluator Demo Scenarios</span>
                <span className="badge-tag bg-orange-100 text-orange-800 border border-orange-200">Official Suite</span>
              </h3>
              <p className="text-xs text-slate-600">Select any pre-loaded scenario to demonstrate SatQuery AI capabilities</p>
            </div>
          </div>

          <button 
            onClick={onClose}
            className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900 transition-all border border-slate-200"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body: Scenarios List */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-slate-50/50">
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
                    ? 'bg-amber-50 border-orange-400 shadow-md shadow-orange-500/10 ring-1 ring-orange-400/40' 
                    : 'bg-white border-slate-200 hover:border-orange-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-mono font-bold text-sm shrink-0 ${
                    isSelected ? 'bg-orange-600 text-white shadow-sm' : 'bg-slate-100 text-slate-600 group-hover:text-orange-600 group-hover:bg-orange-50'
                  }`}>
                    0{idx + 1}
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <h4 className={`text-sm font-bold transition-colors ${isSelected ? 'text-slate-900 font-extrabold' : 'text-slate-800 group-hover:text-orange-600'}`}>
                        {scen.title}
                      </h4>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                        isSelected 
                          ? 'bg-orange-100 text-orange-800 border-orange-200' 
                          : 'bg-slate-100 text-slate-700 border-slate-200'
                      }`}>
                        {scen.badge}
                      </span>
                    </div>

                    <p className={`text-xs mb-2 font-mono leading-relaxed ${isSelected ? 'text-slate-800 font-semibold' : 'text-slate-600'}`}>
                      "{scen.query}"
                    </p>

                    <div className="flex items-center gap-4 text-[11px] text-slate-500 font-mono">
                      <span>Location: <strong className="text-slate-900 font-bold">{scen.location}</strong></span>
                      <span>Date: <strong className="text-slate-900 font-bold">{scen.date}</strong></span>
                    </div>
                  </div>
                </div>

                {/* Select Button */}
                <button className={`btn-primary py-2 px-4 text-xs font-bold shrink-0 ${isSelected ? 'bg-orange-600 text-white hover:bg-orange-700 shadow-md shadow-orange-500/20' : 'bg-slate-900 text-white hover:bg-slate-800'}`}>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>{isSelected ? 'Loaded' : 'Load Demo'}</span>
                </button>
              </div>
            );
          })}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 text-xs text-slate-600 flex items-center justify-between font-mono">
          <span>All scenarios pre-verified with deterministic ground truth</span>
          <button 
            onClick={onClose}
            className="btn-pill-glass py-1.5 px-3 text-xs"
          >
            Close Window
          </button>
        </div>

      </div>
    </div>
  );
}
