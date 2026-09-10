import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import FooterCTA from '../components/FooterCTA';
import { Layers, Activity, Cpu, ArrowLeft, RefreshCw, Calculator } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function IngestionPage({ onOpenDemoModal }) {
  const [b03, setB03] = useState(0.12);
  const [b04, setB04] = useState(0.08);
  const [b08, setB08] = useState(0.45);
  const [b11, setB11] = useState(0.22);

  // Interactive index calculators
  const ndvi = ((b08 - b04) / (b08 + b04)).toFixed(3);
  const ndwi = ((b03 - b08) / (b03 + b08)).toFixed(3);
  const ndbi = ((b11 - b08) / (b11 + b08)).toFixed(3);

  const INDEX_SPECS = [
    { name: "NDVI (Normalized Difference Vegetation Index)", formula: "(NIR - RED) / (NIR + RED)", bands: "B08 (NIR) & B04 (Red)", target: "Vegetation Vigor & Agriculture" },
    { name: "NDWI (Normalized Difference Water Index)", formula: "(GREEN - NIR) / (GREEN + NIR)", bands: "B03 (Green) & B08 (NIR)", target: "Open Surface Water Bodies" },
    { name: "MNDWI (Modified Normalized Difference Water Index)", formula: "(GREEN - SWIR) / (GREEN + SWIR)", bands: "B03 (Green) & B11 (SWIR)", target: "Shadow-Corrected Water" },
    { name: "NDBI (Normalized Difference Built-Up Index)", formula: "(SWIR - NIR) / (SWIR + NIR)", bands: "B11 (SWIR) & B08 (NIR)", target: "Built-up & Urban Structures" },
    { name: "NBR (Normalized Burn Ratio)", formula: "(NIR - SWIR2) / (NIR + SWIR2)", bands: "B08 (NIR) & B12 (SWIR2)", target: "Burned Area Severity" }
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

          <div className="section-tag">RASTER PROCESSING PIPELINE</div>
          <h1 className="heading-font text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">
            Satellite Ingestion & Spectral Index Mathematics
          </h1>
          <p className="text-base text-slate-600 max-w-3xl leading-relaxed">
            Satellite band preparation, cloud masking (SCL), tiling (512x512), and deterministic index formulas calculated in NumPy before LLM interpretation.
          </p>
        </div>

        {/* Interactive Spectral Index Math Calculator */}
        <div className="glass-panel p-6 sm:p-8 border border-slate-200 bg-white shadow-sm space-y-6">
          <div className="flex items-center gap-2">
            <Calculator className="w-5 h-5 text-orange-600" />
            <h2 className="heading-font text-xl font-bold text-slate-900">
              Interactive Band Reflectance & Index Simulator
            </h2>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200">
            <div>
              <label className="text-xs font-mono font-bold text-slate-600 block mb-1">B03 Green: {b03}</label>
              <input type="range" min="0.01" max="0.9" step="0.01" value={b03} onChange={(e) => setB03(Number(e.target.value))} className="w-full accent-orange-600" />
            </div>
            <div>
              <label className="text-xs font-mono font-bold text-slate-600 block mb-1">B04 Red: {b04}</label>
              <input type="range" min="0.01" max="0.9" step="0.01" value={b04} onChange={(e) => setB04(Number(e.target.value))} className="w-full accent-orange-600" />
            </div>
            <div>
              <label className="text-xs font-mono font-bold text-slate-600 block mb-1">B08 NIR: {b08}</label>
              <input type="range" min="0.01" max="0.9" step="0.01" value={b08} onChange={(e) => setB08(Number(e.target.value))} className="w-full accent-orange-600" />
            </div>
            <div>
              <label className="text-xs font-mono font-bold text-slate-600 block mb-1">B11 SWIR: {b11}</label>
              <input type="range" min="0.01" max="0.9" step="0.01" value={b11} onChange={(e) => setB11(Number(e.target.value))} className="w-full accent-orange-600" />
            </div>
          </div>

          {/* Readout */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-center">
            <div className="p-4 rounded-xl bg-orange-50 border border-orange-200">
              <span className="text-xs text-slate-600 font-sans block">Calculated NDVI</span>
              <span className="text-2xl font-bold text-orange-700">{ndvi}</span>
            </div>
            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200">
              <span className="text-xs text-slate-600 font-sans block">Calculated NDWI</span>
              <span className="text-2xl font-bold text-blue-700">{ndwi}</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-100 border border-slate-300">
              <span className="text-xs text-slate-600 font-sans block">Calculated NDBI</span>
              <span className="text-2xl font-bold text-slate-800">{ndbi}</span>
            </div>
          </div>
        </div>

        {/* Index Specifications Table */}
        <div className="glass-panel p-6 sm:p-8 border border-slate-200 bg-white shadow-sm space-y-6">
          <h2 className="heading-font text-2xl font-bold text-slate-900">
            Spectral Index Mathematical Specifications
          </h2>

          <div className="space-y-4">
            {INDEX_SPECS.map((spec, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <h3 className="text-sm font-bold text-slate-900">{spec.name}</h3>
                  <p className="text-xs text-slate-600 font-mono mt-0.5">Formula: <strong className="text-orange-700">{spec.formula}</strong></p>
                  <p className="text-xs text-slate-500 font-sans mt-0.5">Bands Used: {spec.bands}</p>
                </div>
                <span className="text-xs font-mono font-bold px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-800">
                  Target: {spec.target}
                </span>
              </div>
            ))}
          </div>
        </div>

      </main>

      <FooterCTA onOpenDemoModal={onOpenDemoModal} />
    </div>
  );
}
