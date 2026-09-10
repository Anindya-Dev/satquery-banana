import React, { useState } from 'react';
import { ShieldCheck, CheckCircle2, AlertTriangle, Link as LinkIcon, FileText, Database, Layers, Sparkles, ChevronDown, ChevronUp, Lock } from 'lucide-react';

export default function EvidenceGroundingPanel({ scenario }) {
  const [activeTab, setActiveTab] = useState('ANSWER'); // ANSWER | EVIDENCE | GATES

  if (!scenario) return null;

  const conf = scenario.confidence;
  const isHighConf = conf.level === 'HIGH';

  return (
    <div className="glass-panel p-4 flex flex-col h-full border border-slate-200 bg-white shadow-sm relative overflow-hidden">
      
      {/* Panel Header */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-100 text-emerald-800">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 heading-font">Grounded Evidence & Provenance</h3>
            <p className="text-[10px] text-slate-500 font-mono font-medium">Zero Coordinate Hallucination Safeguard</p>
          </div>
        </div>

        {/* Confidence Badge */}
        <div className={`px-3 py-1.5 rounded-xl border flex items-center gap-2 ${
          isHighConf 
            ? 'bg-emerald-50 border-emerald-300 text-emerald-900' 
            : 'bg-orange-50 border-orange-300 text-orange-900'
        }`}>
          <div className="text-right">
            <p className="text-[10px] font-mono uppercase font-bold text-slate-500">Confidence</p>
            <p className="text-xs font-bold font-mono">{conf.level} ({conf.score}%)</p>
          </div>
          <div className="w-7 h-7 rounded-full bg-emerald-700 text-white flex items-center justify-center text-xs font-bold font-mono shadow-sm">
            {conf.score}
          </div>
        </div>
      </div>

      {/* Tabs Switcher */}
      <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200 mb-4 text-xs font-medium">
        <button
          onClick={() => setActiveTab('ANSWER')}
          className={`flex-1 py-1.5 rounded-lg font-bold text-center transition-all ${
            activeTab === 'ANSWER' ? 'bg-orange-600 text-white shadow-sm' : 'text-slate-700 hover:text-slate-950'
          }`}
        >
          Grounded Answer
        </button>
        <button
          onClick={() => setActiveTab('EVIDENCE')}
          className={`flex-1 py-1.5 rounded-lg font-bold text-center transition-all flex items-center justify-center gap-1.5 ${
            activeTab === 'EVIDENCE' ? 'bg-orange-600 text-white shadow-sm' : 'text-slate-700 hover:text-slate-950'
          }`}
        >
          <span>Evidence Chain</span>
          <span className="px-1.5 py-0.2 text-[10px] rounded-full bg-orange-100 text-orange-900 font-mono">
            {scenario.evidenceChain?.length || 0}
          </span>
        </button>
        <button
          onClick={() => setActiveTab('GATES')}
          className={`flex-1 py-1.5 rounded-lg font-bold text-center transition-all flex items-center justify-center gap-1.5 ${
            activeTab === 'GATES' ? 'bg-orange-600 text-white shadow-sm' : 'text-slate-700 hover:text-slate-950'
          }`}
        >
          <span>Validation Gates</span>
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
        </button>
      </div>

      {/* Tab 1: GROUNDED ANSWER */}
      {activeTab === 'ANSWER' && (
        <div className="flex-1 flex flex-col justify-between overflow-y-auto pr-1 space-y-4">
          
          {/* Main Answer Body */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 text-xs sm:text-sm leading-relaxed space-y-2.5 whitespace-pre-line font-sans shadow-inner">
            {scenario.groundedAnswer}
          </div>

          {/* Confidence Factors Breakdown */}
          <div className="p-3.5 rounded-xl bg-white border border-slate-200 space-y-2.5 shadow-sm">
            <h4 className="text-[11px] font-bold text-slate-900 font-mono uppercase tracking-wider flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-orange-600" />
              Deterministic Signal Factors:
            </h4>
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              {Object.entries(conf.factors).map(([key, val]) => (
                <div key={key} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                  <span className="text-slate-500 text-[10px] block capitalize font-sans font-medium">{key.replace(/([A-Z])/g, ' $1')}</span>
                  <span className="font-bold text-orange-700 text-xs">{val}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Provenance Footer Badge */}
          <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-[11px] text-emerald-900 flex items-center justify-between font-mono font-medium">
            <span className="flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-emerald-700" />
              Claims bound to verified spatial raster facts
            </span>
            <span className="text-[10px] text-slate-500 font-bold">EPSG:32645 Verified</span>
          </div>

        </div>
      )}

      {/* Tab 2: EVIDENCE CHAIN */}
      {activeTab === 'EVIDENCE' && (
        <div className="flex-1 overflow-y-auto pr-1 space-y-2.5">
          <p className="text-[11px] text-slate-600 mb-2 font-mono font-medium">
            Auditable provenance records extracted directly from GDAL/Rasterio deterministic math:
          </p>

          {scenario.evidenceChain.map((evid) => (
            <div 
              key={evid.id}
              className="p-3 rounded-xl bg-slate-50 border border-slate-200 hover:border-orange-400 transition-all shadow-sm"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-xs font-bold text-orange-700 flex items-center gap-1.5">
                  <LinkIcon className="w-3.5 h-3.5 text-slate-500" />
                  [{evid.id}]
                </span>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-white text-slate-700 border border-slate-200">
                  {evid.type}
                </span>
              </div>

              <p className="text-xs text-slate-900 font-bold mt-1">{evid.desc}</p>
              
              <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-600 font-mono">
                <span>Source: {evid.source}</span>
                <span className="text-orange-700 font-bold">{evid.value}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 3: VALIDATION GATES */}
      {activeTab === 'GATES' && (
        <div className="flex-1 overflow-y-auto pr-1 space-y-3">
          <p className="text-[11px] text-slate-600 mb-2 font-mono font-medium">
            Hard validation gates enforced before model execution:
          </p>

          {scenario.validationGates.map((gate, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-start gap-3 shadow-sm">
              <div className="p-1 rounded-full bg-emerald-100 text-emerald-800 mt-0.5">
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h5 className="text-xs font-bold text-slate-900">{gate.gate}</h5>
                  <span className="text-[10px] font-mono font-bold text-emerald-800 px-2 py-0.5 rounded bg-emerald-100 border border-emerald-300">
                    {gate.status}
                  </span>
                </div>
                <p className="text-[11px] text-slate-600 font-mono mt-1">{gate.detail}</p>
              </div>
            </div>
          ))}

          {/* Refusal Policy Card */}
          <div className="p-3 rounded-xl bg-orange-50 border border-orange-200 text-xs text-orange-900 space-y-1">
            <h5 className="font-bold flex items-center gap-1.5 text-orange-800">
              <AlertTriangle className="w-3.5 h-3.5" />
              System Refusal Safeguard:
            </h5>
            <p className="text-[11px] text-slate-700 leading-relaxed font-sans">
              If cloud cover exceeds 15% or co-registration shift exceeds 3.0px, the engine immediately yields a structured refusal instead of attempting ungrounded inference.
            </p>
          </div>
        </div>
      )}

    </div>
  );
}
