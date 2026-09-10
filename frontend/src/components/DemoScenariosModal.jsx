import React from 'react';
import { X, Sparkles, CheckCircle2, Play, Layers, Zap, Sliders, ShieldCheck } from 'lucide-react';
import { DEMO_SCENARIOS } from '../data/demoScenarios';

export default function DemoScenariosModal({ isOpen, onClose, onSelectScenario, activeScenarioId }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
      <div className="glass-panel w-full max-w-4xl max-h-[85vh] flex flex-col border border-slate-300 shadow-2xl bg-white overflow-hidden relative rounded-2xl">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-orange-100 text-orange-700 border border-orange-200">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="heading-font text-lg font-bold text-slate-900 flex items-center gap-2">
                <span>SIH Evaluator Demo Scenarios</span>
                <span className="badge-tag bg-orange-100 text-orange-800 border border-orange-200">Official Suite</span>
              </h3>
              <p className="text-xs text-slate-500 font-medium">Select any pre-loaded scenario to demonstrate SatQuery AI capabilities</p>
            </div>
          </div>

          <button 
            onClick={onClose}
            className="p-2 rounded-lg bg-slate-200/80 hover:bg-slate-300 text-slate-600 hover:text-slate-900 transition-all border border-slate-300"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body: Scenarios List */}
        <div className="flex-1 overflow-y-auto p-5 space-y-3.5 bg-slate-50/50">
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
                    ? 'bg-orange-50/90 border-2 border-orange-500 shadow-md' 
                    : 'bg-white border-slate-200 hover:border-orange-400 hover:shadow-sm'
                }`}
              >
                <div className="flex items-start gap-3.5">
                  <div className={`w-9 h-9 rounded-xl flex items-center justify-center font-mono font-bold text-sm shrink-0 ${
                    isSelected ? 'bg-orange-600 text-white' : 'bg-slate-100 text-slate-700 group-hover:bg-orange-100 group-hover:text-orange-900'
                  }`}>
                    0{idx + 1}
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <h4 className="text-sm font-bold text-slate-900 group-hover:text-orange-700 transition-colors">
                        {scen.title}
                      </h4>
                      <span className="text-[10px] font-semibold font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                        {scen.badge}
                      </span>
                    </div>

                    <p className="text-xs text-slate-600 mb-1.5 font-mono">
                      "{scen.query}"
                    </p>

                    <div className="flex items-center gap-4 text-[11px] text-slate-500 font-mono">
                      <span>Location: <strong className="text-slate-800">{scen.location}</strong></span>
                      <span>Date: <strong className="text-slate-800">{scen.date}</strong></span>
                    </div>
                  </div>
                </div>

                {/* Select Button */}
                <button className={`py-2 px-4 rounded-full text-xs font-bold font-mono transition-all shrink-0 flex items-center gap-1.5 ${
                  isSelected 
                    ? 'bg-orange-600 text-white shadow-sm' 
                    : 'bg-slate-900 text-white hover:bg-black'
                }`}>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>{isSelected ? 'Loaded' : 'Load Demo'}</span>
                </button>
              </div>
            );
          })}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-200 bg-white text-xs text-slate-500 flex items-center justify-between font-mono">
          <span>All scenarios pre-verified with deterministic ground truth</span>
          <button 
            onClick={onClose}
            className="btn-pill-glass py-1.5 px-4 text-xs border-slate-300 hover:bg-slate-100"
          >
            Close Window
          </button>
        </div>

      </div>
    </div>
  );
}
