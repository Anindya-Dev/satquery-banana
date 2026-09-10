import React from 'react';
import { CheckCircle2, ShieldCheck } from 'lucide-react';

export default function SIHComplianceChecklist() {
  const REQUIREMENTS = [
    {
      num: "REQ-1",
      title: "Single-Image Analysis & Land Cover",
      desc: "Support natural-language queries over a single remote-sensing image (land-cover, major objects, remote sensing VQA).",
      status: "IMPLEMENTED IN PROTOTYPE"
    },
    {
      num: "REQ-2",
      title: "Visual Grounding & Mask Generation",
      desc: "Identify referenced visual region and produce spatially meaningful segmentation masks / GeoJSON polygons derived from actual raster operations.",
      status: "IMPLEMENTED IN PROTOTYPE"
    },
    {
      num: "REQ-3",
      title: "Bi-Temporal Change VQA — MANDATORY",
      desc: "Image at T1 + Image at T2 → co-registration alignment → change detection → changed regions → change statistics → grounded answer to WHAT and WHERE.",
      status: "IMPLEMENTED IN PROTOTYPE"
    },
    {
      num: "REQ-4",
      title: "Spatial Change Map Generation",
      desc: "Generate georeferenced spatial change map overlays with pixel delta statistics, confidence metrics, and before/after visualization.",
      status: "IMPLEMENTED IN PROTOTYPE"
    },
    {
      num: "REQ-5",
      title: "Cross-Modal Optical + SAR Analysis",
      desc: "Extract complementary information from optical multispectral + SAR radar pairs (Lee despeckling, backscatter roughness, double-bounce detection).",
      status: "IMPLEMENTED IN PROTOTYPE"
    },
    {
      num: "REQ-6",
      title: "Agentic Task Router & Execution Sequencing",
      desc: "Automatically classify intent and select, sequence, and execute appropriate specialist tools according to user query and input configuration.",
      status: "IMPLEMENTED IN PROTOTYPE"
    }
  ];

  return (
    <section className="py-16 px-6 max-w-7xl mx-auto border-t border-slate-200/80">
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="section-tag">SIH COMPLIANCE AUDIT</div>
        <h2 className="heading-font text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          Official Problem Statement Compliance Checklist
        </h2>
        <p className="mt-3 text-base text-slate-600">
          Verification against authoritative product requirements for the SatQuery SIH submission.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {REQUIREMENTS.map((req, idx) => (
          <div key={idx} className="glass-panel p-6 border border-slate-200 bg-white flex flex-col justify-between space-y-4 shadow-sm">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-xs font-bold text-orange-600 px-2 py-0.5 rounded bg-orange-50 border border-orange-200">
                  {req.num}
                </span>
                <span className="text-[10px] font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" />
                  {req.status}
                </span>
              </div>

              <h4 className="heading-font text-lg font-bold text-slate-900 mb-2">
                {req.title}
              </h4>

              <p className="text-xs text-slate-600 leading-relaxed">
                {req.desc}
              </p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
