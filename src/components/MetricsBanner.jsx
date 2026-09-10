import React from 'react';

export default function MetricsBanner() {
  const METRICS = [
    { value: "5 / 5", label: "SIH Demos Supported" },
    { value: "0.0%", label: "Coordinate Fabrications" },
    { value: "< 2.8s", label: "Pipeline Latency" },
    { value: "100%", label: "Evidence Provenance" }
  ];

  return (
    <section id="specs" className="py-16 px-6 max-w-7xl mx-auto border-t border-slate-200/80">
      <div className="glass-panel p-8 sm:p-12 border border-slate-200 text-center relative overflow-hidden bg-white shadow-sm">
        
        <div className="section-tag">VERIFICATION & PERFORMANCE</div>
        <h2 className="heading-font text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-10">
          Deterministic Geospatial Verification Metrics
        </h2>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
          {METRICS.map((m, idx) => (
            <div key={idx} className="p-5 rounded-xl bg-slate-50 border border-slate-200">
              <h3 className="heading-font text-3xl sm:text-4xl font-black text-orange-600 mb-1 font-mono">
                {m.value}
              </h3>
              <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider font-mono">
                {m.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
