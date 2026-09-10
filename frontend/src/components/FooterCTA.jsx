import React from 'react';
import { ArrowRight, Layers, Sparkles } from 'lucide-react';

export default function FooterCTA({ onOpenDemoModal }) {
  return (
    <footer className="pt-16 pb-12 px-6 max-w-7xl mx-auto border-t border-slate-200/80">
      
      {/* Action Banner */}
      <div className="glass-panel-amber p-10 sm:p-14 text-center border border-orange-200 mb-16 relative overflow-hidden bg-orange-50/60 shadow-sm">
        <div className="max-w-3xl mx-auto space-y-5">
          <h2 className="heading-font text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Grounded Remote Sensing Intelligence. <br className="hidden sm:block" />
            Tested & Verified for SIH 2024.
          </h2>

          <p className="text-sm text-slate-600">
            Experience true agentic multimodal satellite analysis grounded in physical satellite physics.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <button 
              onClick={onOpenDemoModal}
              className="btn-amber-glow text-sm"
            >
              <span>Load 5 SIH Evaluator Demos</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <a 
              href="#platform"
              className="btn-pill-glass text-sm border-slate-300 text-slate-800 hover:bg-slate-100"
            >
              <Sparkles className="w-4 h-4 text-orange-600" />
              <span>Launch Interactive Console</span>
            </a>
          </div>
        </div>
      </div>

      {/* Footer Navigation */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-8 pb-12 text-xs font-mono text-slate-600">
        
        <div className="col-span-2 space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
            <div className="w-6 h-6 rounded-lg bg-orange-600 flex items-center justify-center text-white">
              <Layers className="w-3.5 h-3.5" />
            </div>
            <span>SatQuery AI</span>
          </div>
          <p className="text-[11px] text-slate-600 max-w-sm leading-relaxed">
            Agentic Multimodal Remote Sensing Assistant for SIH 2024. Grounded evidence, zero coordinate hallucinations.
          </p>
        </div>

        <div>
          <h4 className="font-bold text-slate-900 mb-3 uppercase tracking-wider">SIH Demos</h4>
          <ul className="space-y-2">
            <li><a href="#platform" className="hover:text-slate-950 transition-colors">Single Image VQA</a></li>
            <li><a href="#platform" className="hover:text-slate-950 transition-colors">Visual Grounding</a></li>
            <li><a href="#platform" className="hover:text-slate-950 transition-colors">Bi-Temporal Change</a></li>
            <li><a href="#platform" className="hover:text-slate-950 transition-colors">Optical + SAR Fusion</a></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-slate-900 mb-3 uppercase tracking-wider">Architecture</h4>
          <ul className="space-y-2">
            <li><a href="#architecture" className="hover:text-slate-950 transition-colors">Task Router</a></li>
            <li><a href="#architecture" className="hover:text-slate-950 transition-colors">Geospatial Layer</a></li>
            <li><a href="#architecture" className="hover:text-slate-950 transition-colors">Validation Gates</a></li>
            <li><a href="#specs" className="hover:text-slate-950 transition-colors">Evidence Chain</a></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-slate-900 mb-3 uppercase tracking-wider">Data Sources</h4>
          <ul className="space-y-2">
            <li><a href="#" className="hover:text-slate-950 transition-colors">Sentinel-2 L2A</a></li>
            <li><a href="#" className="hover:text-slate-950 transition-colors">Sentinel-1 C-SAR</a></li>
            <li><a href="#" className="hover:text-slate-950 transition-colors">Landsat 9 OLI</a></li>
            <li><a href="#" className="hover:text-slate-950 transition-colors">BigEarthNet</a></li>
          </ul>
        </div>

      </div>

      {/* Copyright Line */}
      <div className="border-t border-slate-200/80 pt-6 flex flex-col sm:flex-row items-center justify-between text-[11px] font-mono text-slate-500 gap-2">
        <span>© 2026 SatQuery AI. All rights reserved.</span>
        <span>Built for Smart India Hackathon (SIH) 2024</span>
      </div>

    </footer>
  );
}
