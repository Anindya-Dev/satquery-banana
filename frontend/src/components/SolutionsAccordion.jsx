import React, { useState } from 'react';
import { ArrowRight } from 'lucide-react';

export default function SolutionsAccordion() {
  const [activeTab, setActiveTab] = useState(0);

  const USE_CASES = [
    {
      title: "Disaster Inundation Response",
      desc: "Detect surface water expansion between bi-temporal dates. Computes NDWI deltas (+0.38) and outputs 18.4 km² inundation extent.",
      metric: "18.4 km² Inundation Mask",
      image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80"
    },
    {
      title: "Urban Settlement Sprawl",
      desc: "Analyze built-up growth and land cover composition. Maps NDBI index variations across urban grids and agricultural buffer zones.",
      metric: "+14.2% Settlement Delta",
      image: "https://images.unsplash.com/photo-1541185933-ef5d8ed016c2?auto=format&fit=crop&w=800&q=80"
    },
    {
      title: "Maritime & Port SAR Detection",
      desc: "Fuse Sentinel-1 C-Band SAR radar with optical imagery. Lee despeckling and double-bounce detection highlight structures through heavy cloud cover.",
      metric: "C-Band VV/VH Dual-Pol",
      image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80"
    },
    {
      title: "Agricultural Crop Health",
      desc: "Track multi-seasonal NDVI vegetation health trends (NDVI > 0.45). Detects crop submergence and drought stress across regional basins.",
      metric: "Mean NDVI: +0.42",
      image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80"
    }
  ];

  return (
    <section id="solutions" className="py-16 px-6 max-w-7xl mx-auto border-t border-slate-200/80">
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="section-tag">ANALYSIS DOMAINS</div>
        <h2 className="heading-font text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          Supported Remote Sensing Applications
        </h2>
        <p className="mt-3 text-base text-slate-600">
          Representative test scenarios demonstrating single image, bi-temporal, and optical+SAR capabilities.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {USE_CASES.map((uc, idx) => (
          <div 
            key={idx}
            onClick={() => setActiveTab(idx)}
            className={`glass-panel p-5 border transition-all duration-200 cursor-pointer flex flex-col justify-between bg-white ${
              activeTab === idx 
                ? 'border-orange-500 shadow-md ring-2 ring-orange-400/20' 
                : 'border-slate-200 hover:border-slate-300'
            }`}
          >
            <div>
              <div className="h-36 rounded-lg overflow-hidden mb-3 border border-slate-200 relative">
                <img src={uc.image} alt={uc.title} className="w-full h-full object-cover" />
                <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-slate-900/90 text-[10px] font-mono text-orange-300 border border-slate-700">
                  {uc.metric}
                </div>
              </div>

              <h3 className="heading-font text-base font-bold text-slate-900 mb-1.5">
                {uc.title}
              </h3>

              <p className="text-xs text-slate-600 leading-relaxed font-normal">
                {uc.desc}
              </p>
            </div>

            <div className="pt-4 flex items-center gap-1.5 text-xs font-bold text-orange-600">
              <span>Inspect Scenario</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
