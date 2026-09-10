import React from 'react';
import { Layers, ArrowRight, Sparkles } from 'lucide-react';

export default function Navbar({ onOpenDemoModal, currentScenarioTitle }) {
  return (
    <div className="fixed top-4 inset-x-0 z-50 px-4 max-w-6xl mx-auto">
      <header className="glass-nav px-6 py-3 flex items-center justify-between shadow-lg">
        
        {/* Brand & Logo */}
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-tr from-orange-600 to-amber-500 text-white font-bold shadow-md shadow-orange-500/20">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="heading-font text-base font-extrabold text-slate-900 tracking-tight">
                SatQuery <span className="text-orange-600">AI</span>
              </span>
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-orange-100 text-orange-800 border border-orange-200">
                SIH Prototype
              </span>
            </div>
          </div>
        </div>

        {/* Center Technical Links */}
        <nav className="hidden md:flex items-center gap-6 text-xs font-semibold text-slate-600">
          <a href="#hero" className="hover:text-slate-950 transition-colors">Overview</a>
          <a href="#platform" className="hover:text-slate-950 transition-colors font-bold text-orange-600">Live Engine</a>
          <a href="#requirements" className="hover:text-slate-950 transition-colors">SIH Requirements</a>
          <a href="#architecture" className="hover:text-slate-950 transition-colors">Architecture</a>
          <a href="#specs" className="hover:text-slate-950 transition-colors">Verification Specs</a>
        </nav>

        {/* Action Button */}
        <div className="flex items-center gap-3">
          <button 
            onClick={onOpenDemoModal}
            className="btn-pill-primary text-xs shadow-md"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Load SIH Demos</span>
            <ArrowRight className="w-3 h-3 ml-0.5" />
          </button>
        </div>

      </header>
    </div>
  );
}
