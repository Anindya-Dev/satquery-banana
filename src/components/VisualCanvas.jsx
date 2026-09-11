import React, { useState, useRef, useEffect } from 'react';
import { Eye, EyeOff, Layers, Sliders, Maximize2, RefreshCw, ZoomIn, MapPin, Activity, Sparkles, AlertCircle } from 'lucide-react';

export default function VisualCanvas({ scenario }) {
  const [sliderPos, setSliderPos] = useState(50);
  const [activeLayer, setActiveLayer] = useState('RGB');
  const [showMaskOverlay, setShowMaskOverlay] = useState(true);
  const [sarDespeckle, setSarDespeckle] = useState(true);

  const containerRef = useRef(null);
  const [containerWidth, setContainerWidth] = useState(0);

  useEffect(() => {
    if (!containerRef.current) return;
    const updateSize = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.offsetWidth);
      }
    };
    updateSize();
    const observer = new ResizeObserver(updateSize);
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [scenario]);

  if (!scenario) return null;

  const isBiTemporal = scenario.imageType === 'pair';
  const isOpticalSar = scenario.imageType === 'optical_sar';
  const hasGroundingMask = Boolean(scenario.maskOverlay);

  return (
    <div className="glass-panel p-4 flex flex-col h-full border border-white/10 relative overflow-hidden">
      
      {/* Viewport Header Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 mb-3 border-b border-white/10">
        
        {/* Spatial Title & Location */}
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400">
            <MapPin className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <span>{scenario.location}</span>
              <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-white/5 text-amber-300 border border-white/10">
                {scenario.crs}
              </span>
            </h3>
            <p className="text-[11px] text-slate-400 font-mono">
              BBox: [{scenario.bbox.join(', ')}]
            </p>
          </div>
        </div>

        {/* Layer & Filter Buttons */}
        <div className="flex items-center gap-2">
          
          {/* Spectral Layer Selector */}
          <div className="flex items-center bg-slate-950/80 p-1 rounded-lg border border-white/10 text-xs">
            {['RGB', 'NDVI', 'NDWI', 'NDBI'].map((layer) => (
              <button
                key={layer}
                onClick={() => setActiveLayer(layer)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-semibold font-mono transition-all ${
                  activeLayer === layer
                    ? 'bg-amber-500 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {layer}
              </button>
            ))}
          </div>

          {/* Bi-temporal indicator */}
          {isBiTemporal && (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-mono">
              <Activity className="w-3.5 h-3.5 animate-pulse" />
              <span>Shift: 1.2px (PASSED)</span>
            </div>
          )}

          {/* SAR Despeckle Toggle */}
          {isOpticalSar && (
            <button
              onClick={() => setSarDespeckle(!sarDespeckle)}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-mono transition-all ${
                sarDespeckle 
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                  : 'bg-white/5 text-slate-400 border border-white/10'
              }`}
            >
              <RefreshCw className={`w-3.5 h-3.5 ${sarDespeckle ? 'animate-spin' : ''}`} />
              <span>Lee Filter: {sarDespeckle ? 'ACTIVE' : 'RAW'}</span>
            </button>
          )}

          {/* SAM Mask Toggle */}
          {hasGroundingMask && (
            <button
              onClick={() => setShowMaskOverlay(!showMaskOverlay)}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-mono transition-all ${
                showMaskOverlay
                  ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                  : 'bg-white/5 text-slate-400 border border-white/10'
              }`}
            >
              {showMaskOverlay ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
              <span>SAM Overlay</span>
            </button>
          )}
        </div>

      </div>

      {/* Main Interactive Visual Canvas */}
      <div 
        ref={containerRef}
        className="relative flex-1 min-h-[380px] sm:min-h-[440px] rounded-xl overflow-hidden bg-slate-950 border border-white/10 group"
      >
        
        {/* 1. BI-TEMPORAL SWIPE SLIDER MODE */}
        {isBiTemporal ? (
          <div className="relative w-full h-full select-none overflow-hidden group/slider">
            
            {/* T2 Image (After / Right) - Base Layer */}
            <img 
              src={scenario.imageSecondary} 
              alt="T2 Satellite Scene" 
              className="absolute inset-0 w-full h-full object-cover pointer-events-none"
            />
            <div className="absolute top-3 right-3 z-10 px-2.5 py-1 rounded-md bg-slate-950/80 backdrop-blur border border-white/10 text-[11px] font-mono text-amber-300 pointer-events-none">
              T2: {scenario.endDate || (scenario.sceneDates?.[1]) || 'Post-Event Acquisition'}
            </div>

            {/* T1 Image (Before / Left) - Overflow Clipped Wrapper */}
            <div 
              className="absolute top-0 left-0 bottom-0 overflow-hidden z-10 pointer-events-none"
              style={{ width: `${sliderPos}%` }}
            >
              <img 
                src={scenario.imagePrimary} 
                alt="T1 Satellite Scene" 
                className="absolute top-0 left-0 h-full max-w-none object-cover"
                style={{ width: containerWidth ? `${containerWidth}px` : '100%' }}
              />
              <div className="absolute top-3 left-3 z-10 px-2.5 py-1 rounded-md bg-slate-950/80 backdrop-blur border border-white/10 text-[11px] font-mono text-slate-200 pointer-events-none whitespace-nowrap">
                T1: {scenario.startDate || (scenario.sceneDates?.[0]) || 'Pre-Event Acquisition'}
              </div>
            </div>

            {/* Change Detection Red Overlay Heatmap */}
            {showMaskOverlay && scenario.changeMap && (
              <div className="absolute inset-0 pointer-events-none z-10 mix-blend-screen opacity-65 bg-gradient-to-tr from-red-600/40 via-transparent to-amber-500/20">
                <div className="absolute bottom-14 left-4 p-2.5 rounded-lg bg-slate-950/90 border border-red-500/40 text-xs font-mono text-red-300">
                  <p className="font-bold flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-red-400" />
                    Detected Inundation: {scenario.changeMap.changedAreaKm2} km² ({scenario.changeMap.changeFraction})
                  </p>
                  <p className="text-[10px] text-slate-400 mt-0.5">
                    ΔNDWI: {scenario.changeMap.ndwiDelta} | ΔNDVI: {scenario.changeMap.ndviDelta}
                  </p>
                </div>
              </div>
            )}

            {/* Full-Canvas Interactive Drag Input */}
            <input
              type="range"
              min="0"
              max="100"
              value={sliderPos}
              onChange={(e) => setSliderPos(Number(e.target.value))}
              className="absolute inset-0 w-full h-full opacity-0 z-30 cursor-ew-resize m-0 p-0"
            />

            {/* Visual Divider Line & Center Handle Knob */}
            <div 
              className="absolute top-0 bottom-0 z-20 pointer-events-none"
              style={{ left: `${sliderPos}%` }}
            >
              <div className="w-0.5 h-full bg-amber-500 shadow-[0_0_12px_rgba(245,158,11,0.9)] -ml-[1px]" />
              <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-amber-500 border-2 border-white shadow-2xl flex items-center justify-center text-slate-950 group-hover/slider:scale-110 transition-transform">
                <Sliders className="w-4 h-4" />
              </div>
            </div>
          </div>
        ) : isOpticalSar ? (
          /* 2. OPTICAL + SAR DUAL VIEWPORT MODE */
          <div className="grid grid-cols-1 md:grid-cols-2 w-full h-full gap-1 p-1 bg-slate-950">
            {/* Optical Side */}
            <div className="relative h-full overflow-hidden rounded-lg border border-white/10">
              <img 
                src={scenario.imagePrimary} 
                alt="Optical Scene" 
                className="w-full h-full object-cover"
              />
              <div className="absolute top-3 left-3 px-2.5 py-1 rounded bg-slate-950/80 text-[11px] font-mono text-amber-300 border border-amber-500/20">
                Optical Multispectral (B03/B04/B08)
              </div>
              <div className="absolute bottom-3 left-3 px-2 py-1 rounded bg-slate-950/80 text-[10px] font-mono text-slate-300">
                NDWI: +0.65 | NDBI: +0.42
              </div>
            </div>

            {/* SAR Side */}
            <div className="relative h-full overflow-hidden rounded-lg border border-white/10">
              <img 
                src={scenario.imageSecondary} 
                alt="SAR Intensity Scene" 
                className={`w-full h-full object-cover transition-all ${sarDespeckle ? 'contrast-125 brightness-90 grayscale' : 'brightness-110 contrast-200 grayscale'}`}
              />
              <div className="absolute top-3 left-3 px-2.5 py-1 rounded bg-slate-950/80 text-[11px] font-mono text-emerald-400 border border-emerald-500/20">
                SAR Sentinel-1 ({sarDespeckle ? 'Lee Despeckled' : 'Raw Intensity'})
              </div>
              <div className="absolute bottom-3 left-3 p-2 rounded bg-slate-950/90 text-[10px] font-mono text-slate-300 border border-white/10">
                <span className="text-blue-400 font-bold">Water VV: -21.4 dB</span> | <span className="text-amber-400 font-bold">Urban VH: +6.2 dB</span>
              </div>
            </div>
          </div>
        ) : (
          /* 3. SINGLE IMAGE / VISUAL GROUNDING MODE */
          <div className="relative w-full h-full overflow-hidden">
            <img 
              src={scenario.imagePrimary} 
              alt="Satellite Scene" 
              className={`w-full h-full object-cover transition-all duration-300 ${
                activeLayer === 'NDVI' ? 'hue-rotate-90 saturate-200' :
                activeLayer === 'NDWI' ? 'hue-rotate-180 saturate-200' :
                activeLayer === 'NDBI' ? 'sepia contrast-150' : ''
              }`}
            />
            
            {/* Active Spectral Layer Label */}
            <div className="absolute top-3 left-3 px-2.5 py-1 rounded-md bg-slate-950/80 text-amber-300 border border-white/10 text-[11px] font-mono">
              Active Layer: {activeLayer} Raster Overlay
            </div>

            {/* SAM Grounding Mask Highlight Overlay */}
            {hasGroundingMask && showMaskOverlay && (
              <div className="absolute inset-0 pointer-events-none flex items-center justify-center p-8">
                <div 
                  className="w-3/4 h-3/4 border-2 border-blue-400 rounded-2xl relative animate-pulse"
                  style={{
                    backgroundColor: scenario.maskOverlay.color,
                    borderColor: scenario.maskOverlay.borderColor
                  }}
                >
                  <div className="absolute top-2 left-2 px-2.5 py-1 rounded bg-slate-950/90 text-blue-300 text-xs font-mono font-bold border border-blue-400/50">
                    Target: {scenario.maskOverlay.targetEntity} (IoU: {scenario.maskOverlay.confidenceScore})
                  </div>
                  <div className="absolute bottom-2 right-2 px-2 py-1 rounded bg-slate-950/90 text-white text-[10px] font-mono">
                    Area: {scenario.maskOverlay.areaSqKm} km² | Polygon Verified
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Spectral Index Inspector Footer */}
        {scenario.spectralData && (
          <div className="absolute bottom-3 left-3 right-3 z-20 flex flex-wrap items-center justify-between gap-2 p-2.5 rounded-xl bg-slate-950/90 backdrop-blur text-white border border-white/10 text-xs font-mono">
            <div className="flex items-center gap-4">
              <span className="text-slate-400 flex items-center gap-1 text-[11px]">
                <Activity className="w-3.5 h-3.5 text-amber-400" /> Spectral Readout:
              </span>
              {Object.entries(scenario.spectralData).slice(0, 3).map(([key, val]) => (
                <span key={key} className="text-slate-200">
                  <strong className="text-amber-400">{key}:</strong> {val.avg ?? val.status}
                </span>
              ))}
            </div>

            <div className="flex items-center gap-2 text-[11px] text-emerald-400">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Grounded Evidence Link Active</span>
            </div>
          </div>
        )}

      </div>

    </div>
  );
}
