import React from 'react';
import { ArrowRight, ShieldCheck, Cpu, Database } from 'lucide-react';

export default function DeepFeatureShowcase({ onOpenDemoModal }) {
  const ARCHITECTURE_FEATURES = [
    {
      num: "01",
      tag: "ORCHESTRATION LAYER",
      title: "Agentic Task Router & Tool Dispatch",
      description: "Determines whether the user request is single-image analysis, visual grounding, bi-temporal change, or optical+SAR fusion — sequencing specialist tools deterministically without ungrounded autonomous loops.",
      image: "https://images.unsplash.com/photo-1541185933-ef5d8ed016c2?auto=format&fit=crop&w=800&q=80",
      cta: "View Router Logic"
    },
    {
      num: "02",
      tag: "GEOSPATIAL LAYER",
      title: "Deterministic Pre-Filter & Raster Operations",
      description: "All spectral indices (NDVI, NDWI, NDBI) and bi-temporal pixel deltas are calculated in GDAL/Rasterio before passing evidence to the VLM. The LLM interprets evidence; it never fabricates numbers.",
      image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80",
      cta: "Inspect Raster Math"
    },
    {
      num: "03",
      tag: "EVIDENCE & REFUSAL LAYER",
      title: "Claim-to-Evidence Validation & Refusal Gates",
      description: "Every claim string must cite verified evidence_ids. If cloud cover exceeds 15% or co-registration shift exceeds 3.0px, the engine immediately yields a structured refusal instead of hallucinating.",
      image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80",
      cta: "View Validation Gates"
    }
  ];

  return (
    <section id="architecture" className="py-16 px-6 max-w-7xl mx-auto border-t border-slate-200/80">
      
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
        <div>
          <div className="section-tag">SYSTEM ARCHITECTURE</div>
          <h2 className="heading-font text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Hallucination Prevention Architecture
          </h2>
        </div>
        <p className="text-sm text-slate-600 max-w-md">
          How SatQuery AI separates reasoning (LLM) from execution (deterministic geospatial code).
        </p>
      </div>

      {/* Feature List */}
      <div className="space-y-8">
        {ARCHITECTURE_FEATURES.map((feat, idx) => {
          const isReverse = idx % 2 === 1;

          return (
            <div 
              key={idx}
              className={`glass-panel p-6 sm:p-8 border border-slate-200 bg-white grid grid-cols-1 lg:grid-cols-12 gap-8 items-center ${
                isReverse ? 'lg:flex-row-reverse' : ''
              }`}
            >
              {/* Text Side */}
              <div className={`lg:col-span-6 space-y-3 ${isReverse ? 'lg:order-2' : 'lg:order-1'}`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-orange-600 uppercase tracking-wider">
                    {feat.tag}
                  </span>
                  <span className="heading-font text-2xl font-extrabold text-slate-300 font-mono">
                    {feat.num}
                  </span>
                </div>

                <h3 className="heading-font text-2xl font-bold text-slate-900 leading-tight">
                  {feat.title}
                </h3>

                <p className="text-sm text-slate-600 leading-relaxed font-normal">
                  {feat.description}
                </p>

                <div className="pt-2">
                  <a 
                    href="#platform"
                    className="btn-pill-glass text-xs font-bold border-slate-300 hover:bg-slate-100 inline-flex items-center gap-1.5 cursor-pointer"
                  >
                    <span>{feat.cta}</span>
                    <ArrowRight className="w-3 h-3 text-orange-600" />
                  </a>
                </div>
              </div>

              {/* Visual Side */}
              <div className={`lg:col-span-6 ${isReverse ? 'lg:order-1' : 'lg:order-2'}`}>
                <div className="relative w-full h-60 sm:h-72 rounded-xl overflow-hidden border border-slate-200">
                  <img 
                    src={feat.image} 
                    alt={feat.title} 
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute bottom-3 left-3 px-3 py-1.5 rounded-lg bg-slate-900/90 text-white text-[11px] font-mono border border-slate-700">
                    Verified Execution Gate Active
                  </div>
                </div>
              </div>

            </div>
          );
        })}
      </div>

    </section>
  );
}
