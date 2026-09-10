import React from 'react';
import { ArrowRight, Check } from 'lucide-react';

export default function EvaluatorSuiteSection({ onOpenDemoModal }) {
  const TIERS = [
    {
      name: "Single-Image & Grounding",
      desc: "Ideal for basic land-cover VQA and SAM visual grounding.",
      badge: "PROTOTYPE TIER",
      features: [
        "Single Scene VQA reasoning",
        "SAM ViT-H mask segmentation",
        "Spectral Index Calculations (NDVI/NDWI)",
        "Grounded Evidence JSON output"
      ],
      highlight: false
    },
    {
      name: "SIH Evaluator Suite (Loaded)",
      desc: "Perfect for hackathon presentation with full 5 demo scenarios.",
      badge: "RECOMMENDED",
      features: [
        "All 5 SIH mandatory demo scenarios",
        "OpenCV bi-temporal co-registration",
        "Sentinel-1 SAR Lee despeckle filter",
        "Deterministic task router engine",
        "Zero coordinate hallucination guarantee"
      ],
      highlight: true
    },
    {
      name: "Distributed Enterprise Grid",
      desc: "Designed for multi-region continuous satellite stream ingestion.",
      badge: "PRODUCTION",
      features: [
        "PostGIS + MinIO object storage",
        "Background worker queue (RQ/arq)",
        "Copernicus streaming API discovery",
        "Priority GPU VLM inference fleet"
      ],
      highlight: false
    }
  ];

  return (
    <section className="py-16 px-6 max-w-7xl mx-auto">
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="section-tag">EVALUATOR SUITE</div>
        <h2 className="heading-font text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
          Flexible deployment options.
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {TIERS.map((tier, idx) => (
          <div 
            key={idx}
            className={`glass-panel p-8 border flex flex-col justify-between relative ${
              tier.highlight 
                ? 'glass-panel-amber border-amber-500/60 shadow-2xl scale-105 z-10' 
                : 'border-white/10'
            }`}
          >
            {tier.highlight && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-amber-500 text-black text-[10px] font-extrabold uppercase font-mono tracking-wider">
                Most Popular for Judges
              </div>
            )}

            <div>
              <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest block mb-1">
                {tier.badge}
              </span>
              <h3 className="heading-font text-2xl font-bold text-white mb-2">{tier.name}</h3>
              <p className="text-xs text-slate-300 mb-6">{tier.desc}</p>

              <ul className="space-y-3 mb-8">
                {tier.features.map((feat, fidx) => (
                  <li key={fidx} className="flex items-center gap-2 text-xs text-slate-200 font-mono">
                    <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>{feat}</span>
                  </li>
                ))}
              </ul>
            </div>

            <button 
              onClick={onOpenDemoModal}
              className={tier.highlight ? 'btn-amber-glow w-full justify-center text-xs' : 'btn-pill-glass w-full justify-center text-xs'}
            >
              <span>Load Suite</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
