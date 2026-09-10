import React from 'react';
import Navbar from '../components/Navbar';
import FooterCTA from '../components/FooterCTA';
import { Database, FileText, ArrowLeft, ShieldCheck, Code } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function DataContractsPage({ onOpenDemoModal }) {
  const CONTRACTS = [
    {
      name: "Image",
      purpose: "Represents a single user-provided satellite scene or crop.",
      fields: ["id: str", "filename: str", "path: Path", "modality: Modality", "crs: Optional[CRS]", "bbox: Optional[BBox]", "width: int", "height: int", "band_count: int"]
    },
    {
      name: "ImagePair",
      purpose: "Validated image pair for bi-temporal change or optical+SAR fusion.",
      fields: ["id: str", "image_t1: Image", "image_t2: Image", "pair_type: PairType", "co_registration_quality: CoRegistrationQuality", "spatial_overlap_fraction: float"]
    },
    {
      name: "CoRegistrationQuality",
      purpose: "Result of spatial alignment validation gate before pixel math.",
      fields: ["status: GateStatus (PASSED/FAILED)", "method: str", "translation_pixels: float", "rotation_deg: float", "overlap_fraction: float"]
    },
    {
      name: "Evidence",
      purpose: "Grounding carrier for machine-checkable factual claims.",
      fields: ["id: str", "type: EvidenceType", "source_image_id: str", "acquisition_date: Optional[date]", "bbox: Optional[BBox]", "value: Union[float, dict]", "desc: str"]
    },
    {
      name: "Confidence",
      purpose: "Deterministic quality score derived from measurable signals.",
      fields: ["level: ConfidenceLevel (HIGH/MED/LOW)", "score: int (0-100)", "factors: dict", "reasons: List[str]"]
    },
    {
      name: "SegmentationMask",
      purpose: "Output of SAM visual grounding or spatial region extraction.",
      fields: ["id: str", "mask_path: Path", "polygon_geojson: dict", "confidence_score: float", "area_sq_km: float"]
    },
    {
      name: "ChangeMap",
      purpose: "Output of bi-temporal change detection specialist.",
      fields: ["id: str", "changed_area_km2: float", "change_fraction: float", "ndwi_delta: float", "ndvi_delta: float", "change_mask_path: Path"]
    }
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

          <div className="section-tag font-mono">DOMAIN OBJECT SPECIFICATIONS</div>
          <h1 className="heading-font text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">
            Data Contracts & Pydantic Schemas
          </h1>
          <p className="text-base text-slate-600 max-w-3xl leading-relaxed">
            Minimum domain objects required for auditable geospatial evidence grounding, validation gates, and Pydantic request/response parsing.
          </p>
        </div>

        {/* Contracts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {CONTRACTS.map((c, idx) => (
            <div key={idx} className="glass-panel p-6 border border-slate-200 bg-white shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="heading-font text-xl font-bold text-slate-900 flex items-center gap-2">
                  <Code className="w-5 h-5 text-orange-600" />
                  {c.name}
                </h3>
                <span className="text-[10px] font-mono font-bold px-2.5 py-1 rounded bg-slate-100 text-slate-700 border border-slate-200">
                  Domain Object
                </span>
              </div>

              <p className="text-xs text-slate-600 font-sans">{c.purpose}</p>

              <div className="p-3.5 rounded-xl bg-slate-900 text-emerald-400 font-mono text-xs space-y-1 overflow-x-auto">
                <p className="text-slate-400 text-[10px] uppercase font-bold">// Fields & Types</p>
                {c.fields.map((f, fidx) => (
                  <p key={fidx}>{f}</p>
                ))}
              </div>
            </div>
          ))}
        </div>

      </main>

      <FooterCTA onOpenDemoModal={onOpenDemoModal} />
    </div>
  );
}
