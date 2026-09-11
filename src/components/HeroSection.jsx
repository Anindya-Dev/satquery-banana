import React from 'react';
import { ArrowRight, Sparkles, ShieldCheck, Layers, Activity, FileCheck } from 'lucide-react';

export default function HeroSection({ onOpenDemoModal, onScrollToPlatform }) {
  return (
    <section id="hero" className="relative pt-32 pb-16 px-6 max-w-7xl mx-auto text-center md:text-left overflow-hidden">
      
      {/* Background Soft Glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-gradient-to-r from-orange-400/10 via-amber-300/10 to-transparent blur-[140px] pointer-events-none rounded-full"></div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
        
        {/* Left Column: Technical Overview */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* SIH Prototype Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-orange-50 border border-orange-200 text-xs text-orange-900 font-semibold font-mono shadow-sm">
            <FileCheck className="w-4 h-4 text-orange-600" />
            <span>SIH 2024 Problem Statement Compliant Prototype</span>
          </div>

          {/* Academic/Technical Headline */}
          <h1 className="heading-font text-3xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.15]">
            Multimodal Remote Sensing Intelligence through <span className="text-orange-600">Natural Queries.</span>
          </h1>

          {/* Subtext Description */}
          <p className="text-base sm:text-lg text-slate-600 max-w-2xl font-normal leading-relaxed">
            An agentic vision-language assistant for single-image analysis, SAM visual grounding, bi-temporal change detection, and optical+SAR fusion — grounded strictly in verified geospatial physics with zero fabricated coordinates.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center justify-center md:justify-start gap-4 pt-2">
            <button 
              onClick={onScrollToPlatform}
              className="btn-amber-glow text-sm shadow-lg"
            >
              <span>Test Live Engine</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Technical Validation Badges */}
          <div className="pt-4 flex flex-wrap items-center gap-4 text-xs text-slate-600 font-mono">
            <div className="flex items-center gap-1.5 bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Deterministic Validation Gates</span>
            </div>
            <div className="flex items-center gap-1.5 bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm">
              <Activity className="w-4 h-4 text-orange-600" />
              <span>Sentinel-1 SAR + Sentinel-2 Optical</span>
            </div>
          </div>

        </div>

        {/* Right Column: Satellite Raster Technical Frame */}
        <div className="lg:col-span-5 relative flex justify-center">
          <div className="relative w-full max-w-md aspect-square rounded-3xl overflow-hidden glass-panel p-4 border border-slate-200 shadow-xl bg-white">
            <img 
              src="https://images.unsplash.com/photo-1541185933-ef5d8ed016c2?auto=format&fit=crop&w=800&q=80" 
              alt="Satellite Scene" 
              className="w-full h-full object-cover rounded-2xl"
            />
            
            {/* Technical Badges Overlay */}
            <div className="absolute top-8 left-8 p-3 rounded-xl bg-slate-900/90 backdrop-blur-md border border-slate-700 text-xs font-mono text-white shadow-lg">
              <p className="text-amber-400 font-bold flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" /> Sentinel-2 L2A Active
              </p>
              <p className="text-slate-300 text-[11px] mt-0.5">Bands: B02, B03, B04, B08, B11</p>
            </div>

            <div className="absolute bottom-8 right-8 p-3 rounded-xl bg-slate-900/90 backdrop-blur-md border border-slate-700 text-xs font-mono text-white shadow-lg text-right">
              <p className="text-emerald-400 font-bold">Confidence: HIGH (96%)</p>
              <p className="text-slate-300 text-[11px] mt-0.5">EPSG:32645 Verified</p>
            </div>
          </div>
        </div>

      </div>

    </section>
  );
}
