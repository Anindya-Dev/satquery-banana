// SatQuery AI — Official SIH Evaluator Demo Scenarios Dataset

export const DEMO_SCENARIOS = [
  {
    id: "demo-1",
    title: "Demo 1: Single Image VQA & Land Cover",
    badge: "Single Image",
    task: "SINGLE_IMAGE_VQA",
    query: "Describe the land-cover composition and major visible geographic features in this coastal satellite scene.",
    location: "Kolkata Coastal Region, India",
    date: "2024-04-15",
    crs: "EPSG:32645 (UTM Zone 45N)",
    bbox: [88.214, 22.451, 88.482, 22.689],
    imageType: "single",
    imagePrimary: "/assets/kolkata_coastal.png",
    imageSecondary: null,
    maskOverlay: null,
    spectralData: {
      NDVI: { avg: 0.42, max: 0.78, min: -0.15, status: "Dense Vegetation & Mangroves" },
      NDWI: { avg: 0.18, max: 0.85, min: -0.45, status: "Active River Network Detected" },
      NDBI: { avg: 0.12, max: 0.55, min: -0.32, status: "Moderate Urban Settlement" }
    },
    confidence: {
      level: "HIGH",
      score: 96,
      factors: {
        validPixels: "99.4%",
        cloudCoverage: "0.6%",
        spectralSanity: "Passed (100%)",
        spatialMatch: "Exact Footprint"
      },
      reasons: ["Zero cloud obstruction", "Full band spectrum available (Sentinel-2 L2A)", "Verified spatial metadata"]
    },
    groundedAnswer: `Based on deterministic spectral indices and high-resolution Sentinel-2 observations:
    
• **Land Cover Distribution**: 48% dense agricultural/mangrove vegetation (NDVI > 0.45), 28% water bodies including the Hooghly estuary (NDWI > 0.35), 18% urban built-up area (NDBI 0.15 to 0.55), and 6% mudflats/barren soil.
• **Major Objects**: Hooghly river channel, port logistics zone, urban grid, and coastal vegetation buffers.
• **Evidence Verification**: All spectral index distributions fall within physical boundaries [-1.0, 1.0]. No cloud masking interference detected.`,
    evidenceChain: [
      { id: "EVID-101", type: "IMAGE_METADATA", source: "Sentinel-2A L2A Tile T45QXF", value: "2024-04-15T05:22:10Z", desc: "Copernicus Open Access Hub Verified" },
      { id: "EVID-102", type: "SPECTRAL_INDEX", source: "Rasterio Band Calculation (B04, B08)", value: "Mean NDVI: +0.42", desc: "48% Area Vegetation Coverage" },
      { id: "EVID-103", type: "SPECTRAL_INDEX", source: "Rasterio Band Calculation (B03, B08)", value: "Mean NDWI: +0.18", desc: "Estuarine Surface Water Signature" },
      { id: "EVID-104", type: "GEOSPATIAL_CRS", source: "GDAL Metadata Inspection", value: "EPSG:32645 WGS 84 / UTM 45N", desc: "Sub-meter Spatial Transform Verified" }
    ],
    validationGates: [
      { gate: "Input Validity", status: "PASSED", detail: "Valid Sentinel-2 L2A GeoTIFF" },
      { gate: "Cloud Cover Gate", status: "PASSED", detail: "0.6% < 15% threshold" },
      { gate: "Spectral Sanity", status: "PASSED", detail: "All values within physical range [-1, 1]" },
      { gate: "Claim Verification", status: "PASSED", detail: "4/4 claims linked to verified evidence IDs" }
    ]
  },
  {
    id: "demo-2",
    title: "Demo 2: Visual Grounding & SAM Segmentation",
    badge: "Visual Grounding",
    task: "VISUAL_GROUNDING",
    query: "Highlight the primary water body referred to in the query and generate a spatial mask.",
    location: "Sunderbans Estuarine Basin",
    date: "2024-05-02",
    crs: "EPSG:4326 (WGS84)",
    bbox: [88.612, 21.890, 88.945, 22.120],
    imageType: "single",
    imagePrimary: "/assets/kolkata_coastal.png",
    imageSecondary: null,
    maskOverlay: {
      type: "SAM_SEGMENTATION",
      targetEntity: "Estuarine Water Channel",
      areaSqKm: 42.8,
      confidenceScore: 0.94,
      polygonGeoJSON: "Polygon (((88.65 21.92, 88.82 21.95, 88.80 22.05, 88.64 22.02, 88.65 21.92)))",
      color: "rgba(59, 130, 246, 0.45)",
      borderColor: "#3b82f6"
    },
    spectralData: {
      NDWI: { avg: 0.76, max: 0.92, min: 0.45, status: "High Purity Water Mask" },
      MNDWI: { avg: 0.81, max: 0.95, min: 0.52, status: "Shadow-Corrected Open Water" }
    },
    confidence: {
      level: "HIGH",
      score: 94,
      factors: {
        validPixels: "98.8%",
        samSegmentationIoU: "0.91",
        spectralMatch: "MNDWI > 0.50 Threshold",
        spatialMatch: "Exact GeoJSON Polygon"
      },
      reasons: ["SAM ViT-H mask boundary aligned with MNDWI threshold", "Zero coordinate hallucination", "Grounded to physical pixel raster"]
    },
    groundedAnswer: `The target water body has been segmented using SAM (Segment Anything Model) paired with deterministic MNDWI spectral thresholding:
    
• **Identified Entity**: Sunderbans Main Estuarine Tidal Channel.
• **Spatial Extent**: 42.8 km² polygon surface area bounded within [88.612°E, 21.890°N to 88.945°E, 22.120°N].
• **Grounding Verification**: Mask derived directly from raster pixel operations (MNDWI > 0.50) intersected with SAM neural segment boundaries. Coordinates exported as valid GeoJSON.`,
    evidenceChain: [
      { id: "EVID-201", type: "SAM_MASK", source: "SAM ViT-H Neural Segmentor", value: "IoU Confidence: 0.91", desc: "42.8 km² Polygon Boundary Extracted" },
      { id: "EVID-202", type: "SPECTRAL_INDEX", source: "Rasterio Band (B03, B11 MNDWI)", value: "Mean MNDWI: +0.81", desc: "Water Body Spectral Signature Confirmed" },
      { id: "EVID-203", type: "GEOJSON_POLYGON", source: "GDAL Vectorization Engine", value: "EPSG:4326 GeoJSON Geometry", desc: "Grounded Polygon Coordinates" }
    ],
    validationGates: [
      { gate: "Grounding Target Gate", status: "PASSED", detail: "Target 'water body' successfully resolved to SAM prompt" },
      { gate: "Segmentation IoU Gate", status: "PASSED", detail: "0.91 > 0.80 quality threshold" },
      { gate: "Geospatial Export Gate", status: "PASSED", detail: "Valid WGS84 GeoJSON geometry" }
    ]
  },
  {
    id: "demo-3",
    title: "Demo 3: Mandatory Bi-Temporal Change VQA",
    badge: "Bi-Temporal Change",
    task: "CHANGE_DETECTION",
    query: "What changed between these two dates (2023-09-10 vs 2024-09-10), and where did the change occur?",
    location: "Kolkata Inundation & Urban Expansion Zone",
    date: "T1: 2023-09-10 | T2: 2024-09-10",
    crs: "EPSG:32645 (UTM Zone 45N)",
    bbox: [88.300, 22.500, 88.450, 22.650],
    imageType: "pair",
    imagePrimary: "/assets/kolkata_coastal.png", // T1 Before
    imageSecondary: "/assets/bitemporal_t2.png", // T2 After
    coRegistration: {
      status: "PASSED",
      method: "OpenCV ECC Phase Correlation",
      maxPixelShift: "1.2 px",
      rotationDeg: "0.02°",
      overlapFraction: "98.6%",
      qualityScore: "EXCELLENT"
    },
    changeMap: {
      changedAreaKm2: 18.4,
      changeFraction: "14.2% of Scene",
      dominantType: "Surface Water Inundation & Vegetation Submergence",
      ndwiDelta: "+0.38",
      ndviDelta: "-0.29",
      colorOverlay: "rgba(239, 68, 68, 0.5)"
    },
    spectralData: {
      NDWI_T1: { avg: 0.12, status: "Normal Baseline Water" },
      NDWI_T2: { avg: 0.50, status: "Post-Monsoon Inundation Spike" },
      NDVI_T1: { avg: 0.58, status: "Dense Green Canopy" },
      NDVI_T2: { avg: 0.29, status: "Submerged Agricultural Land" }
    },
    confidence: {
      level: "HIGH",
      score: 95,
      factors: {
        coRegistrationShift: "1.2px (Excellent)",
        spatialOverlap: "98.6%",
        temporalGap: "365 Days (Normalized Seasonality)",
        validPixels: "99.1%"
      },
      reasons: ["Passed co-registration alignment gate (shift < 3px)", "Significant NDWI delta (+0.38) backed by pixel math", "No cloud interference in T1 or T2"]
    },
    groundedAnswer: `Co-registered bi-temporal analysis between 2023-09-10 (T1) and 2024-09-10 (T2):

• **WHAT Changed**: Major surface water expansion (inundation) covering 18.4 km² (14.2% of the scene area). Average NDWI increased by +0.38 while NDVI dropped by -0.29 due to crop field submergence.
• **WHERE it Changed**: The change is heavily concentrated in the eastern floodplain corridor [88.38°E to 88.44°E, 22.54°N to 22.62°N].
• **Deterministic Validation**: Co-registration alignment passed with only 1.2px shift. The change map is derived from pixel-level delta computation (|NDWI_T2 - NDWI_T1| > 0.30) and confirmed by morphological filtering.`,
    evidenceChain: [
      { id: "EVID-301", type: "COREGISTRATION", source: "OpenCV ECC Phase Alignment", value: "Shift: 1.2px, Overlap: 98.6%", desc: "Spatial Alignment Gate PASSED" },
      { id: "EVID-302", type: "RASTER_DIFF", source: "NumPy Pixel Delta (|T2 - T1|)", value: "ΔNDWI: +0.38", desc: "18.4 km² Flood Inundation Mask Generated" },
      { id: "EVID-303", type: "CHANGE_STATS", source: "Rasterio Spatial Statistics", value: "14.2% Total Change Area", desc: "Statistically Verified Delta Threshold" }
    ],
    validationGates: [
      { gate: "Co-Registration Alignment", status: "PASSED", detail: "1.2px shift < 3.0px limit" },
      { gate: "Temporal Validity Gate", status: "PASSED", detail: "Valid bi-temporal pairing T1 & T2" },
      { gate: "Spatial Overlap Gate", status: "PASSED", detail: "98.6% > 85% requirement" }
    ]
  },
  {
    id: "demo-4",
    title: "Demo 4: Required Optical + SAR Multimodal Fusion",
    badge: "Optical + SAR",
    task: "OPTICAL_SAR_FUSION",
    query: "Use the optical and SAR images together to identify built-up structures and water-covered regions.",
    location: "Hooghly River & Urban Industrial Complex",
    date: "2024-03-20",
    crs: "EPSG:32645 (UTM Zone 45N)",
    bbox: [88.250, 22.480, 88.420, 22.620],
    imageType: "optical_sar",
    imagePrimary: "/assets/kolkata_coastal.png", // Optical
    imageSecondary: "/assets/sar_sentinel1.png", // SAR (despeckled intensity)
    sarPreprocessed: {
      speckleFilter: "Enhanced Lee Filter (5x5 Window)",
      calibration: "Sigma0 (σº) Radiometric dB Scale",
      polarization: "VV + VH Dual-Pol",
      backscatterWater: "< -18 dB (Specular Reflection)",
      backscatterUrban: "> +4 dB (Double-Bounce Scattering)"
    },
    spectralData: {
      NDWI_Optical: { avg: 0.65, status: "Optical Surface Water Signature" },
      SAR_VV_Water: { avg: -21.4, unit: "dB", status: "Radar Smooth Surface Specular Reflection" },
      NDBI_Optical: { avg: 0.42, status: "Optical Built-up Signature" },
      SAR_VH_Urban: { avg: +6.2, unit: "dB", status: "Radar Structural Double-Bounce" }
    },
    confidence: {
      level: "HIGH",
      score: 97,
      factors: {
        modalityComplementarity: "Optical Spectral + SAR Backscatter",
        sarSpeckleFilter: "Lee Filter 5x5 Applied",
        coRegistration: "Sub-pixel Match",
        validPixels: "99.7%"
      },
      reasons: ["SAR despeckling verified", "Water bodies confirmed by BOTH optical NDWI (>0.5) and SAR VV (<-18dB)", "Built-up structures confirmed by SAR double-bounce (>+4dB) penetrating thin cloud cover"]
    },
    groundedAnswer: `Multimodal fusion of Sentinel-2 Multispectral Optical and Sentinel-1 SAR (Synthetic Aperture Radar) data:

• **Water Covered Regions**: Conclusively identified by combining Optical NDWI (+0.65) with SAR VV backscatter (-21.4 dB specular reflection). Dark SAR regions perfectly match optical water bodies with zero cloud confusion.
• **Built-Up Industrial Structures**: Identified via SAR VH double-bounce (+6.2 dB) which highlights metal roofs and concrete walls, paired with Optical NDBI (+0.42).
• **Physical Modality Synergy**: SAR microwave signals penetrated light overcast haze, providing true physical surface roughness data complementing optical spectral bands.`,
    evidenceChain: [
      { id: "EVID-401", type: "SAR_PREPROCESSING", source: "Lee Speckle Filter (5x5)", value: "Sigma0 VV: -21.4 dB (Water)", desc: "Radiometrically Calibrated Radar Backscatter" },
      { id: "EVID-402", type: "OPTICAL_INDEX", source: "Sentinel-2 B03/B08 NDWI", value: "NDWI: +0.65", desc: "Multispectral Surface Water Confirmation" },
      { id: "EVID-403", type: "MULTIMODAL_FUSION", source: "Cross-Modality Verification Gate", value: "Optical NDWI ∩ SAR Specular", desc: "100% Modality Agreement for Surface Features" }
    ],
    validationGates: [
      { gate: "Modality Preprocessing", status: "PASSED", detail: "SAR Lee Despeckling & Sigma0 Calibration Applied" },
      { gate: "Cross-Modality Co-Registration", status: "PASSED", detail: "Sub-pixel Grid Alignment Verified" },
      { gate: "Complementary Fusion Gate", status: "PASSED", detail: "Dual optical-radar feature extraction active" }
    ]
  },
  {
    id: "demo-5",
    title: "Demo 5: Agentic Task Router & Execution Sequencing",
    badge: "Agentic Router",
    task: "AGENTIC_ROUTING",
    query: "Auto-detect intent: 'Compare these two dates and highlight where new water bodies appeared.'",
    location: "Dynamic Request Router Engine",
    date: "Real-time Execution",
    crs: "EPSG:32645",
    bbox: [88.200, 22.400, 88.500, 22.700],
    imageType: "pair",
    imagePrimary: "/assets/kolkata_coastal.png",
    imageSecondary: "/assets/bitemporal_t2.png",
    routingResult: {
      detectedTask: "BI_TEMPORAL_CHANGE + VISUAL_GROUNDING",
      selectedSpecialists: ["Co-Registration Specialist", "Change Detection Specialist", "SAM Grounding Specialist"],
      executionPipeline: [
        { step: 1, name: "Query Parsing & Intent Extraction", status: "COMPLETED", duration: "120ms" },
        { step: 2, name: "Input Configuration Validation", status: "COMPLETED", duration: "45ms" },
        { step: 3, name: "Co-Registration Alignment Gate", status: "COMPLETED", duration: "310ms" },
        { step: 4, name: "Change Mask Generation", status: "COMPLETED", duration: "450ms" },
        { step: 5, name: "SAM Segmentation Grounding", status: "COMPLETED", duration: "820ms" },
        { step: 6, name: "Evidence Assembly & Grounded VLM Answer", status: "COMPLETED", duration: "1150ms" }
      ]
    },
    spectralData: {
      RoutingConfidence: { avg: 0.98, status: "Deterministic Rule Match" }
    },
    confidence: {
      level: "HIGH",
      score: 98,
      factors: {
        intentParser: "100% Schema Match",
        specialistSequence: "Validated Dependency Order",
        executionLatency: "2.89s Total"
      },
      reasons: ["Router selected correct specialist pipeline without autonomous loops", "All validation gates passed in sequence"]
    },
    groundedAnswer: `Agentic Task Router automatically categorized the request and executed the following specialist sequence:

1. **Intent Parsed**: User requested bi-temporal comparison AND visual grounding ('highlight').
2. **Specialist Pipeline Sequenced**:
   • Co-Registration Specialist validated T1/T2 alignment (1.2px shift).
   • Change Detection Specialist isolated newly inundated pixels (ΔNDWI > +0.35).
   • Grounding Specialist executed SAM segmentation on the change mask to output a vector GeoJSON polygon.
3. **Execution Summary**: Total pipeline executed deterministically in 2.89s with 100% evidence provenance.`,
    evidenceChain: [
      { id: "EVID-501", type: "ROUTER_LOG", source: "Task Router Intent Classifier", value: "Intent: CHANGE_DETECTION + GROUNDING", desc: "Automatic Specialist Dispatch" },
      { id: "EVID-502", type: "PIPELINE_EXEC", source: "Deterministic Orchestrator", value: "6/6 Stages Executed", desc: "Zero Ungrounded LLM Loop Errors" }
    ],
    validationGates: [
      { gate: "Task Classification Gate", status: "PASSED", detail: "Matched CHANGE_DETECTION + GROUNDING" },
      { gate: "Specialist Dependency Gate", status: "PASSED", detail: "Co-Registration ran BEFORE Change Detection" },
      { gate: "Evidence Aggregation Gate", status: "PASSED", detail: "Combined evidence payload created" }
    ]
  }
];
