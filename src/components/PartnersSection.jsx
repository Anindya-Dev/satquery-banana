import React from 'react';

export default function PartnersSection() {
  const SATELLITES = [
    { name: "Sentinel-2", tag: "ESA Copernicus 10m Multispectral" },
    { name: "Sentinel-1", tag: "C-Band Synthetic Aperture Radar" },
    { name: "Landsat 9", tag: "USGS Operational Land Imager" },
    { name: "PlanetScope", tag: "3m High-Frequency Constellation" },
    { name: "Maxar WorldView", tag: "30cm Very High Resolution" },
    { name: "BigEarthNet", tag: "Multimodal Deep Learning Benchmark" }
  ];

  return (
    <section className="py-10 px-6 max-w-7xl mx-auto text-center border-t border-slate-200/80">
      <div className="section-tag">EARTH OBSERVATION DATASETS</div>
      <h3 className="heading-font text-lg sm:text-xl font-bold text-slate-800 mb-6">
        Supported Satellite Constellations & Remote Sensing Repositories
      </h3>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        {SATELLITES.map((s, idx) => (
          <div 
            key={idx}
            className="p-3.5 rounded-xl bg-white border border-slate-200 hover:border-orange-400 hover:shadow-md transition-all duration-200 group flex flex-col items-center justify-center text-center shadow-sm"
          >
            <h4 className="heading-font text-sm font-bold text-slate-900 group-hover:text-orange-600 transition-colors">
              {s.name}
            </h4>
            <p className="text-[10px] text-slate-500 font-mono mt-1 leading-tight">
              {s.tag}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
