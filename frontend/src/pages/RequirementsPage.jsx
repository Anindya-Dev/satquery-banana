import React from 'react';
import Navbar from '../components/Navbar';
import FooterCTA from '../components/FooterCTA';
import { CheckCircle2, ShieldCheck, ArrowLeft, FileText } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function RequirementsPage({ onOpenDemoModal }) {
  const MATRIX = [
    { req: "1. Natural-language query understanding", status: "IMPLEMENTED", detail: "LiteLLM + Pydantic constrained query intent parser" },
    { req: "2. Single-image remote-sensing VQA", status: "IMPLEMENTED", detail: "LLaVA / InternVL VLM with spectral indices context" },
    { req: "3. Land-cover understanding", status: "IMPLEMENTED", detail: "NDVI, NDWI, NDBI index thresholding" },
    { req: "4. Object/region understanding", status: "IMPLEMENTED", detail: "Spatial region bbox resolution" },
    { req: "5. Visual grounding", status: "IMPLEMENTED", detail: "Segment Anything Model (SAM) promptable segmentor" },
    { req: "6. Segmentation/mask generation", status: "IMPLEMENTED", detail: "Raster mask to GeoJSON polygon converter" },
    { req: "7. Bi-temporal image handling", status: "IMPLEMENTED", detail: "T1/T2 paired image input pipeline" },
    { req: "8. Image co-registration", status: "IMPLEMENTED", detail: "OpenCV ECC Phase Correlation alignment gate" },
    { req: "9. Change detection", status: "IMPLEMENTED", detail: "Pixel diff + thresholding + morphological cleanup" },
    { req: "10. Change VQA", status: "IMPLEMENTED", detail: "Grounded reasoning over T1, T2 & change mask" },
    { req: "11. Spatial change map", status: "IMPLEMENTED", detail: "Raster overlay + changed area km² calculation" },
    { req: "12. Optical preprocessing", status: "IMPLEMENTED", detail: "Rasterio band normalization & Sentinel-2 SCL cloud mask" },
    { req: "13. SAR preprocessing", status: "IMPLEMENTED", detail: "Lee 5x5 speckle filter & Sigma0 dB calibration" },
    { req: "14. Optical-SAR co-registration", status: "IMPLEMENTED", detail: "Cross-modality grid transform validation" },
    { req: "15. Optical-SAR fusion", status: "IMPLEMENTED", detail: "Optical spectral + SAR backscatter complementary features" },
    { req: "16. Multimodal reasoning", status: "IMPLEMENTED", detail: "VLM side-by-side optical & SAR prompt interpretation" },
    { req: "17. Agentic task routing", status: "IMPLEMENTED", detail: "Rule-based & LLM intent classifier router" },
    { req: "18. Specialist model execution", status: "IMPLEMENTED", detail: "Specialist interface contracts for VQA/Grounding/Change/Fusion" },
    { req: "19. User-provided single image", status: "IMPLEMENTED", detail: "FastAPI upload endpoint with format validation" },
    { req: "20. User-provided image pair", status: "IMPLEMENTED", detail: "Paired upload with temporal metadata" },
    { req: "21. User-provided optical + SAR pair", status: "IMPLEMENTED", detail: "Modality auto-detection heuristic" },
    { req: "22. Geospatial correctness", status: "IMPLEMENTED", detail: "Zero LLM coordinate fabrication policy" },
    { req: "23. CRS management", status: "IMPLEMENTED", detail: "WGS84 / UTM CRS transform via GDAL" },
    { req: "24. Provenance tracking", status: "IMPLEMENTED", detail: "Auditable evidence payload attached to all claims" },
    { req: "25. Evidence grounding", status: "IMPLEMENTED", detail: "ClaimValidator checks evidence_id links" },
    { req: "26. Confidence scoring", status: "IMPLEMENTED", detail: "Deterministic multi-signal scoring function" },
    { req: "27. Refusal / failure handling", status: "IMPLEMENTED", detail: "Structured refusal when cloud >15% or shift >3px" },
    { req: "28. Reliability & error handling", status: "IMPLEMENTED", detail: "Explicit validation gates" },
    { req: "29. Observability", status: "IMPLEMENTED", detail: "Per-stage latency and provenance logging" },
    { req: "30. Scalability roadmap", status: "IMPLEMENTED", detail: "Monolith-to-Worker migration ADR" },
    { req: "31. SIH demo feasibility", status: "IMPLEMENTED", detail: "5 pre-loaded evaluator demo scenarios" }
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

          <div className="section-tag">CAPABILITY GAP MATRIX</div>
          <h1 className="heading-font text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">
            31-Point SIH Verification Matrix
          </h1>
          <p className="text-base text-slate-600 max-w-3xl leading-relaxed">
            Audit evaluation verifying all product requirements established in the official SIH problem statement.
          </p>
        </div>

        {/* Matrix Table */}
        <div className="glass-panel p-6 sm:p-8 border border-slate-200 bg-white shadow-sm space-y-4 overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-xs font-mono font-bold text-slate-500 uppercase">
                <th className="py-3 px-4"># Requirement</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Implementation Evidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-xs font-mono">
              {MATRIX.map((m, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  <td className="py-3.5 px-4 font-bold text-slate-900 font-sans text-sm">{m.req}</td>
                  <td className="py-3.5 px-4">
                    <span className="px-2.5 py-1 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold text-[10px] inline-flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" />
                      {m.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-600 font-sans">{m.detail}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </main>

      <FooterCTA onOpenDemoModal={onOpenDemoModal} />
    </div>
  );
}
