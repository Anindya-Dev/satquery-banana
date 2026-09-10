import React from 'react';
import Navbar from '../components/Navbar';
import FooterCTA from '../components/FooterCTA';
import { ShieldCheck, Cpu, Database, Activity, Lock, Layers, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function ArchitecturePage({ onOpenDemoModal }) {
  const LAYERS = [
    { num: 1, title: "Structured Query Extraction", prevents: "LLM inventing free-form, unvalidatable intent", technology: "Constrained JSON Schema via LiteLLM" },
    { num: 2, title: "Deterministic Geospatial Pre-Filter", prevents: "Wrong-location imagery being used as evidence", technology: "Shapely BBox Intersection & CRS Transform" },
    { num: 3, title: "Deterministic Spectral Calculation", prevents: "Fabricated index numbers (NDVI/NDWI/NDBI)", technology: "NumPy / Rasterio Pixel Band Math" },
    { num: 4, title: "Metadata & Cloud Mask Quality Gate", prevents: "Answering from cloud-covered or corrupted pixels", technology: "Sentinel-2 SCL Cloud Masking (Gate 2)" },
    { num: 5, title: "Evidence-Only Prompt Construction", prevents: "Model reaching for external parametric knowledge", technology: "Strict System Prompting with Pre-Filtered Tiles" },
    { num: 6, title: "Structured Model Output Schema", prevents: "Free-form prose claims without Machine-Checkable IDs", technology: "Pydantic Schema with claims + evidence_ids" },
    { num: 7, title: "Claim-to-Evidence Post-Validation", prevents: "Claims citing non-existent evidence or unsupported causal language", technology: "Regex Causal Downgrade & Evidence ID Lookup" },
    { num: 8, title: "Deterministic Confidence Scoring", prevents: "Overconfident framing when data is marginal", technology: "Multi-signal Scoring (Valid %, Shift, Cloud %)" },
    { num: 9, title: "Pre-VLM Evidence Sufficiency Check", prevents: "Calling VLM when data is insufficient (skips inference entirely)", technology: "Sufficiency Threshold Check (Gate 9)" },
    { num: 10, title: "First-Class Refusal Path", prevents: "Fabricated answers from thin data", technology: "Explicit Refusal Object ('Insufficient Evidence')" },
    { num: 11, title: "Full Provenance Tracking", prevents: "Un-auditable outputs", technology: "Immutable Tile ID + Scene + Date + CRS Links" }
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      <Navbar onOpenDemoModal={onOpenDemoModal} />

      <main className="pt-28 pb-16 px-6 max-w-7xl mx-auto space-y-12">
        
        {/* Page Header */}
        <div className="space-y-4">
          <Link to="/" className="inline-flex items-center gap-1.5 text-xs font-mono font-bold text-orange-600 hover:text-orange-800">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Console
          </Link>

          <div className="section-tag">ENGINEERING DESIGN SPECIFICATION</div>
          <h1 className="heading-font text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">
            11-Layer Hallucination Prevention Architecture
          </h1>
          <p className="text-base text-slate-600 max-w-3xl leading-relaxed">
            The core design philosophy of SatQuery AI: <em>The LLM/VLM is an interpreter and explainer, never a source of fact.</em> Every geographic, temporal, and spectral fact originates from deterministic code.
          </p>
        </div>

        {/* 11 Layers Table / Grid */}
        <div className="glass-panel p-6 sm:p-8 border border-slate-200 bg-white shadow-sm space-y-6">
          <h2 className="heading-font text-2xl font-bold text-slate-900 flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-orange-600" />
            Layered Safeguard Architecture
          </h2>

          <div className="space-y-4">
            {LAYERS.map((layer) => (
              <div key={layer.num} className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-start gap-3">
                  <span className="w-8 h-8 rounded-lg bg-orange-600 text-white font-mono font-bold text-xs flex items-center justify-center shrink-0">
                    L{layer.num}
                  </span>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">{layer.title}</h3>
                    <p className="text-xs text-slate-600 font-medium">Prevents: <strong className="text-orange-800">{layer.prevents}</strong></p>
                  </div>
                </div>

                <div className="text-xs font-mono font-bold px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 shrink-0">
                  {layer.technology}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ADR Section */}
        <div className="glass-panel p-6 sm:p-8 border border-slate-200 bg-white shadow-sm space-y-4">
          <div className="section-tag">ARCHITECTURE DECISION RECORD (ADR)</div>
          <h2 className="heading-font text-2xl font-bold text-slate-900">
            Selected Option: Modular Monolith + Task Router
          </h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            Evaluating candidate designs for the 36-hour SIH prototype: Architecture 1 (Pure Monolith), Architecture 2 (Monolith + Background Worker), and Architecture 3 (Microservices).
          </p>
          <div className="p-4 rounded-xl bg-orange-50 border border-orange-200 text-xs font-mono text-orange-950 space-y-1">
            <p className="font-bold">Decision Summary:</p>
            <p>Monolith + Task Router wins on build speed, deterministic execution guarantees, and testability — avoiding message broker overhead while keeping ingestion isolated from query serving.</p>
          </div>
        </div>

      </main>

      <FooterCTA onOpenDemoModal={onOpenDemoModal} />
    </div>
  );
}
