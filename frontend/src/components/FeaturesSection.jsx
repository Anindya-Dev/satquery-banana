import React from 'react';
import { Zap, Sliders, Sparkles, ArrowRight } from 'lucide-react';

export default function FeaturesSection({ onSelectTask }) {
  const REQUIREMENTS = [
    {
      id: "CHANGE_DETECTION",
      tag: "MANDATORY REQUIREMENT 3",
      title: "Bi-Temporal Change VQA",
      description: "Co-registered image at T1 + image at T2 → spatial validation → change detection mask → change statistics → grounded answer to WHAT changed and WHERE.",
      image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80",
      icon: Zap,
      accent: "text-orange-600 border-orange-200"
    },
    {
      id: "VISUAL_GROUNDING",
      tag: "REQUIREMENT 2",
      title: "Visual Grounding & SAM Masks",
      description: "Identify referenced visual region and produce spatially meaningful segmentation masks, raster overlays, or GeoJSON polygons without coordinate fabrication.",
      image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=600&q=80",
      icon: Sliders,
      accent: "text-blue-600 border-blue-200"
    },
    {
      id: "OPTICAL_SAR_FUSION",
      tag: "REQUIREMENT 5",
      title: "Cross-Modal Optical + SAR",
      description: "Extract complementary features combining co-registered optical multispectral data with SAR radar backscatter to resolve built-up and surface water features.",
      image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80",
      icon: Sparkles,
      accent: "text-emerald-600 border-emerald-200"
    }
  ];

  return (
    <section id="requirements" className="py-16 px-6 max-w-7xl mx-auto border-t border-slate-200/80">
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="section-tag">SIH PROBLEM STATEMENT REQUIREMENTS</div>
        <h2 className="heading-font text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          Core Multimodal Analysis Capabilities
        </h2>
        <p className="mt-3 text-base text-slate-600">
          The prototype implements specialized tools and deterministic validation gates to fulfill all authoritative product requirements.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {REQUIREMENTS.map((req) => {
          const Icon = req.icon;

          return (
            <div 
              key={req.id}
              onClick={() => onSelectTask(req.id)}
              className="glass-panel p-6 border border-slate-200 hover:border-orange-500 hover:shadow-lg transition-all duration-250 group cursor-pointer flex flex-col justify-between bg-white"
            >
              <div>
                {/* Image Container */}
                <div className="relative w-full h-44 rounded-xl overflow-hidden mb-5 border border-slate-200">
                  <img 
                    src={req.image} 
                    alt={req.title} 
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-3 left-3 px-2.5 py-1 rounded-md bg-slate-900/90 text-[10px] font-mono font-bold text-orange-300 border border-slate-700">
                    {req.tag}
                  </div>
                </div>

                {/* Title */}
                <div className="flex items-center gap-2 mb-2">
                  <Icon className={`w-5 h-5 ${req.accent}`} />
                  <h3 className="heading-font text-xl font-bold text-slate-900 group-hover:text-orange-600 transition-colors">
                    {req.title}
                  </h3>
                </div>

                {/* Description */}
                <p className="text-sm text-slate-600 leading-relaxed font-normal">
                  {req.description}
                </p>
              </div>

              {/* Action Link */}
              <div className="pt-6 flex items-center gap-2 text-xs font-bold text-orange-600 group-hover:translate-x-1 transition-transform">
                <span>Test Specialist Specialist</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
