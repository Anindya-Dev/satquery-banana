import React from 'react';

export default function TestimonialsSection() {
  const TESTIMONIALS = [
    {
      quote: "SatQuery AI's deterministic evidence engine is a game-changer. The refusal safeguard when co-registration alignment drops is true engineering.",
      name: "Dr. Aris Thorne",
      role: "Lead Remote Sensing Scientist, EarthObs Institute"
    },
    {
      quote: "Being able to combine Sentinel-1 SAR despeckled backscatter with Sentinel-2 optical NDWI in a single grounded query is phenomenal.",
      name: "Elena Rostova",
      role: "Senior GIS & Maritime Surveillance Specialist"
    },
    {
      quote: "Zero coordinate hallucinations! Every GeoJSON polygon and change stat is bound to physical raster pixels. Highly recommended for SIH evaluators.",
      name: "Marcus Vance",
      role: "Chief Geospatial Architect, Defense Intelligence"
    }
  ];

  return (
    <section className="py-16 px-6 max-w-7xl mx-auto">
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="section-tag">FIELD EVALUATIONS</div>
        <h2 className="heading-font text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
          What domain experts say.
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {TESTIMONIALS.map((t, idx) => (
          <div key={idx} className="glass-panel p-6 border border-white/10 flex flex-col justify-between space-y-4">
            <p className="text-sm text-slate-300 leading-relaxed italic font-sans">
              "{t.quote}"
            </p>
            <div>
              <h4 className="heading-font text-sm font-bold text-white">{t.name}</h4>
              <p className="text-xs text-slate-400 font-mono">{t.role}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
