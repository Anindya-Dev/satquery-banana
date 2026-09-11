import React, { useState } from 'react';
import { ShieldCheck, CheckCircle2, AlertTriangle, Link as LinkIcon, FileText, Database, Layers, Sparkles, ChevronDown, ChevronUp, Lock, Network } from 'lucide-react';
import GraphifyModal from './GraphifyModal';

export default function EvidenceGroundingPanel({ scenario }) {
  const [activeTab, setActiveTab] = useState('ANSWER'); // ANSWER | EVIDENCE | GATES
  const [expandedEvidence, setExpandedEvidence] = useState(null);
  const [isGraphifyOpen, setIsGraphifyOpen] = useState(false);

  if (!scenario) return null;

  const conf = scenario.confidence;
  const isHighConf = conf.level === 'HIGH';

  return (
    <div className="glass-panel p-4 flex flex-col h-full border border-white/10 relative overflow-hidden">
      
      {/* Graphify Modal Container */}
      <GraphifyModal 
        isOpen={isGraphifyOpen} 
        onClose={() => setIsGraphifyOpen(false)} 
        scenarioData={scenario}
      />

      {/* Panel Header */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white heading-font">Grounded Intelligence & Evidence</h3>
            <p className="text-[10px] text-slate-400 font-mono">Zero Hallucination Guarantee</p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsGraphifyOpen(true)}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-slate-900 text-indigo-300 hover:text-white hover:bg-slate-800 border border-slate-700 text-xs font-mono font-bold transition-all shadow-sm group"
            title="Launch Graphify Knowledge Graph Visualizer"
          >
            <Network className="w-3.5 h-3.5 text-indigo-400 group-hover:animate-spin" />
            <span>Graphify View</span>
          </button>

          {/* Confidence Gauge Badge */}
          <div className={`px-3 py-1.5 rounded-xl border flex items-center gap-2 ${
            isHighConf 
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' 
              : 'bg-amber-500/10 border-amber-500/30 text-amber-300'
          }`}>
            <div className="text-right">
              <p className="text-[10px] font-mono uppercase text-slate-400">Confidence</p>
              <p className="text-xs font-bold font-mono">{conf.level} ({conf.score}%)</p>
            </div>
            <div className="w-8 h-8 rounded-full bg-slate-950 flex items-center justify-center border border-white/10 text-xs font-bold font-mono text-emerald-400">
              {conf.score}
            </div>
          </div>
        </div>
      </div>


      {/* Tabs Switcher */}
      <div className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-lg border border-white/10 mb-4 text-xs">
        <button
          onClick={() => setActiveTab('ANSWER')}
          className={`flex-1 py-1.5 rounded-md font-semibold text-center transition-all ${
            activeTab === 'ANSWER' ? 'bg-amber-500 text-white shadow' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Grounded Answer
        </button>
        <button
          onClick={() => setActiveTab('EVIDENCE')}
          className={`flex-1 py-1.5 rounded-md font-semibold text-center transition-all flex items-center justify-center gap-1 ${
            activeTab === 'EVIDENCE' ? 'bg-amber-500 text-white shadow' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>Evidence Chain</span>
          <span className="px-1.5 py-0.2 text-[10px] rounded-full bg-white/20 font-mono">
            {scenario.evidenceChain?.length || 0}
          </span>
        </button>
        <button
          onClick={() => setActiveTab('GATES')}
          className={`flex-1 py-1.5 rounded-md font-semibold text-center transition-all flex items-center justify-center gap-1 ${
            activeTab === 'GATES' ? 'bg-amber-500 text-white shadow' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>Validation Gates</span>
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
        </button>
      </div>

      {/* Tab 1: GROUNDED ANSWER */}
      {activeTab === 'ANSWER' && (
        <div className="flex-1 flex flex-col justify-between overflow-y-auto pr-1 space-y-4">
          
          {/* Main Answer Body */}
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-white/5 text-xs sm:text-sm text-slate-200 leading-relaxed space-y-2 whitespace-pre-line font-sans">
            {scenario.groundedAnswer}
          </div>

          {/* Confidence Factors Breakdown */}
          <div className="p-3 rounded-xl bg-white/5 border border-white/10 space-y-2">
            <h4 className="text-[11px] font-bold text-slate-300 font-mono uppercase tracking-wider flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
              Deterministic Signal Factors:
            </h4>
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              {Object.entries(conf.factors).map(([key, val]) => (
                <div key={key} className="p-2 rounded bg-slate-950/80 border border-white/5">
                  <span className="text-slate-400 text-[10px] block capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                  <span className="font-semibold text-amber-300">{val}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Provenance Footer Badge */}
          <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-[11px] text-emerald-300 flex items-center justify-between font-mono">
            <span className="flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-emerald-400" />
              Claims bound to verified spatial raster facts
            </span>
            <span className="text-[10px] text-slate-400">EPSG:32645 Verified</span>
          </div>

        </div>
      )}

      {/* Tab 2: EVIDENCE CHAIN */}
      {activeTab === 'EVIDENCE' && (
        <div className="flex-1 overflow-y-auto pr-1 space-y-2.5">
          <p className="text-[11px] text-slate-400 mb-2 font-mono">
            Auditable provenance records extracted directly from GDAL/Rasterio deterministic math:
          </p>

          {scenario.evidenceChain.map((evid) => (
            <div 
              key={evid.id}
              onClick={() => setExpandedEvidence(expandedEvidence === evid.id ? null : evid.id)}
              className="p-3 rounded-xl bg-slate-950/80 border border-white/10 hover:border-amber-500/40 transition-all cursor-pointer"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-xs font-bold text-amber-400 flex items-center gap-1.5">
                  <LinkIcon className="w-3.5 h-3.5 text-slate-400" />
                  [{evid.id}]
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-slate-300">
                  {evid.type}
                </span>
              </div>

              <p className="text-xs text-white font-semibold">{evid.desc}</p>
              
              <div className="mt-1 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                <span>Source: {evid.source}</span>
                <span className="text-amber-300 font-bold">{evid.value}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 3: VALIDATION GATES */}
      {activeTab === 'GATES' && (
        <div className="flex-1 overflow-y-auto pr-1 space-y-3">
          <p className="text-[11px] text-slate-400 mb-2 font-mono">
            Hard validation gates enforced before model execution:
          </p>

          {scenario.validationGates.map((gate, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-slate-950/80 border border-white/10 flex items-start gap-3">
              <div className="p-1 rounded-full bg-emerald-500/20 text-emerald-400 mt-0.5">
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h5 className="text-xs font-bold text-white">{gate.gate}</h5>
                  <span className="text-[10px] font-mono font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                    {gate.status}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 font-mono mt-1">{gate.detail}</p>
              </div>
            </div>
          ))}

          {/* Refusal Policy Card */}
          <div className="p-3 rounded-xl bg-amber-500/5 border border-amber-500/20 text-xs text-amber-200 space-y-1">
            <h5 className="font-bold flex items-center gap-1.5 text-amber-300">
              <AlertTriangle className="w-3.5 h-3.5" />
              System Refusal Safeguard:
            </h5>
            <p className="text-[11px] text-slate-300">
              If cloud cover exceeds 15% or co-registration shift exceeds 3.0px, the engine immediately yields a structured refusal instead of attempting ungrounded inference.
            </p>
          </div>
        </div>
      )}

    </div>
  );
}
