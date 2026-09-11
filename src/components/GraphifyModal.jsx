import React, { useState, useEffect, useRef } from 'react';
import { 
  X, ZoomIn, ZoomOut, RotateCcw, Download, Network, Filter, Info, 
  Layers, CheckCircle, Database, Cpu, Activity, ShieldCheck, Sparkles 
} from 'lucide-react';

const NODE_CONFIG = {
  QUERY: { color: '#3B82F6', border: '#60A5FA', icon: Cpu, label: 'Query' },
  LOCATION: { color: '#10B981', border: '#34D399', icon: Layers, label: 'Location' },
  TILE: { color: '#8B5CF6', border: '#A78BFA', icon: Database, label: 'Raster Scene' },
  SPECTRAL_METRIC: { color: '#F59E0B', border: '#FBBF24', icon: Activity, label: 'Spectral Index' },
  EVIDENCE: { color: '#06B6D4', border: '#22D3EE', icon: ShieldCheck, label: 'Evidence Item' },
  CLAIM: { color: '#EC4899', border: '#F472B6', icon: CheckCircle, label: 'Validated Claim' },
  CONFIDENCE: { color: '#6366F1', border: '#818CF8', icon: Sparkles, label: 'Confidence' },
};

export default function GraphifyModal({ isOpen, onClose, scenarioData }) {
  const [graphData, setGraphData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [activeFilters, setActiveFilters] = useState(
    Object.keys(NODE_CONFIG).reduce((acc, key) => ({ ...acc, [key]: true }), {})
  );
  const [nodePositions, setNodePositions] = useState({});
  const [draggingNode, setDraggingNode] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const containerRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return;

    const payload = scenarioData || {
      query_text: "Analyze Sentinel-2 NDWI and NDVI spectral evidence across region of interest",
      location_name: "Kolkata Coastal Zone (22.57° N, 88.36° E)",
      bbox: [88.2, 22.4, 88.5, 22.7],
      candidate_tiles: [
        {
          tile_id: "tile-s2-kolkata-01",
          sensor: "Sentinel-2 MSI",
          acquisition_time: "2024-05-20",
          cloud_cover: 2.4,
          metrics: { ndwi: 0.4852, ndvi: 0.2104, mndwi: 0.5120 }
        }
      ],
      evidence_chain: [
        {
          evidence_id: "ev-901",
          description: "Deterministic NDWI reflectance spike (+0.4852) indicates significant inundated surface expansion."
        }
      ],
      validated_claims: [
        {
          claim: "High-confidence detection of 14.2% water surface area expansion following heavy precipitation.",
          confidence: 0.96
        }
      ],
      confidence: 0.96
    };

    const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
    fetch(`${API_BASE_URL}/api/v1/graphify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then((res) => res.json())
      .then((data) => {
        setGraphData(data);
        calculateInitialPositions(data.nodes);
      })
      .catch(() => {
        const mockGraph = generateMockGraph(payload);
        setGraphData(mockGraph);
        calculateInitialPositions(mockGraph.nodes);
      });
  }, [isOpen, scenarioData]);

  const calculateInitialPositions = (nodes) => {
    if (!nodes || nodes.length === 0) return;
    const center = { x: 380, y: 280 };
    const pos = {};

    const queryNodes = nodes.filter(n => n.type === 'QUERY');
    const locNodes = nodes.filter(n => n.type === 'LOCATION');
    const tileNodes = nodes.filter(n => n.type === 'TILE');
    const metricNodes = nodes.filter(n => n.type === 'SPECTRAL_METRIC');
    const evNodes = nodes.filter(n => n.type === 'EVIDENCE');
    const claimNodes = nodes.filter(n => n.type === 'CLAIM');
    const confNodes = nodes.filter(n => n.type === 'CONFIDENCE');

    queryNodes.forEach((n) => { pos[n.id] = { x: center.x, y: 70 }; });
    locNodes.forEach((n, i) => { pos[n.id] = { x: center.x - 180 + i * 360, y: 150 }; });
    tileNodes.forEach((n, i) => {
      const step = 600 / (tileNodes.length + 1);
      pos[n.id] = { x: step * (i + 1), y: 240 };
    });
    metricNodes.forEach((n, i) => {
      const step = 660 / (metricNodes.length + 1);
      pos[n.id] = { x: step * (i + 1), y: 340 };
    });
    evNodes.forEach((n, i) => {
      const step = 600 / (evNodes.length + 1);
      pos[n.id] = { x: step * (i + 1), y: 430 };
    });
    claimNodes.forEach((n, i) => { pos[n.id] = { x: center.x - 120 + i * 240, y: 500 }; });
    confNodes.forEach((n) => { pos[n.id] = { x: center.x, y: 560 }; });

    setNodePositions(pos);
  };

  const generateMockGraph = (data) => {
    const q_text = data.query_text || "Satellite Imagery Query";
    return {
      graphify_version: "0.9.58",
      query_id: "q-demo",
      stats: { node_count: 7, edge_count: 8, density: 0.19, communities: 1 },
      nodes: [
        { id: "q-1", label: `Query: ${q_text.slice(0, 30)}...`, type: "QUERY", color: "#3B82F6", metadata: { text: q_text } },
        { id: "loc-1", label: `Location: ${data.location_name || "Kolkata"}`, type: "LOCATION", color: "#10B981", metadata: { name: data.location_name } },
        { id: "tile-1", label: "Tile: Sentinel-2 MSI", type: "TILE", color: "#8B5CF6", metadata: { sensor: "Sentinel-2 MSI", date: "2024-05-20" } },
        { id: "metric-1", label: "Index: NDWI = 0.4852", type: "SPECTRAL_METRIC", color: "#F59E0B", metadata: { metric: "NDWI", value: 0.4852 } },
        { id: "ev-1", label: "Evidence: NDWI surface water spike", type: "EVIDENCE", color: "#06B6D4", metadata: { desc: "NDWI reflectance spike" } },
        { id: "claim-1", label: "Claim: 14.2% inundated area growth", type: "CLAIM", color: "#EC4899", metadata: { text: "14.2% expansion" } },
        { id: "conf-1", label: "Confidence: HIGH (96%)", type: "CONFIDENCE", color: "#6366F1", metadata: { score: 0.96 } }
      ],
      edges: [
        { source: "q-1", target: "loc-1", relationship: "LOCATED_AT" },
        { source: "loc-1", target: "tile-1", relationship: "CONTAINS_TILE" },
        { source: "tile-1", target: "metric-1", relationship: "CALCULATED_METRIC" },
        { source: "metric-1", target: "ev-1", relationship: "PROVIDES_EVIDENCE" },
        { source: "q-1", target: "ev-1", relationship: "GROUNDED_IN" },
        { source: "ev-1", target: "claim-1", relationship: "SUPPORTS_CLAIM" },
        { source: "claim-1", target: "conf-1", relationship: "SCORED_WITH" }
      ]
    };
  };

  const handleMouseDownNode = (e, nodeId) => {
    e.stopPropagation();
    setDraggingNode(nodeId);
    const pos = nodePositions[nodeId] || { x: 300, y: 300 };
    setDragOffset({ x: e.clientX - pos.x, y: e.clientY - pos.y });
  };

  const handleMouseMoveCanvas = (e) => {
    if (!draggingNode) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(40, Math.min(rect.width - 40, e.clientX - rect.left));
    const y = Math.max(40, Math.min(rect.height - 40, e.clientY - rect.top));
    setNodePositions((prev) => ({ ...prev, [draggingNode]: { x, y } }));
  };

  const handleMouseUpCanvas = () => {
    setDraggingNode(null);
  };

  const toggleFilter = (type) => {
    setActiveFilters((prev) => ({ ...prev, [type]: !prev[type] }));
  };

  const exportJSON = () => {
    if (!graphData) return;
    const blob = new Blob([JSON.stringify(graphData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `graphify-knowledge-graph-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  const visibleNodes = graphData?.nodes?.filter((n) => activeFilters[n.type]) || [];
  const visibleNodeIds = new Set(visibleNodes.map((n) => n.id));
  const visibleEdges = graphData?.edges?.filter((e) => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target)) || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-6xl h-[88vh] bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/90">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-indigo-400">
              <Network className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-bold text-white tracking-wide">Graphify Knowledge Graph</h3>
                <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-mono border border-indigo-500/30">
                  v0.9.58 Engine
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Interactive spatial-spectral evidence graph & claim topology
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setZoomLevel((z) => Math.min(1.5, z + 0.1))}
              className="p-2 text-slate-400 hover:text-white bg-slate-800/60 hover:bg-slate-800 rounded-lg border border-slate-700/50 transition-colors"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={() => setZoomLevel((z) => Math.max(0.6, z - 0.1))}
              className="p-2 text-slate-400 hover:text-white bg-slate-800/60 hover:bg-slate-800 rounded-lg border border-slate-700/50 transition-colors"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={() => { setZoomLevel(1); calculateInitialPositions(graphData?.nodes); }}
              className="p-2 text-slate-400 hover:text-white bg-slate-800/60 hover:bg-slate-800 rounded-lg border border-slate-700/50 transition-colors"
              title="Reset Layout"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              onClick={exportJSON}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition-colors border border-indigo-400/30 shadow-lg shadow-indigo-600/20"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Graph</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Layout */}
        <div className="flex-1 flex overflow-hidden relative">
          <div 
            ref={containerRef}
            className="flex-1 bg-slate-950 relative overflow-hidden select-none cursor-crosshair"
            onMouseMove={handleMouseMoveCanvas}
            onMouseUp={handleMouseUpCanvas}
            style={{
              backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.05) 1px, transparent 0)',
              backgroundSize: '24px 24px'
            }}
          >
            <svg 
              className="w-full h-full absolute inset-0 pointer-events-none transition-transform duration-75"
              style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center center' }}
            >
              <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569" />
                </marker>
              </defs>
              {visibleEdges.map((edge) => {
                const sourcePos = nodePositions[edge.source] || { x: 200, y: 200 };
                const targetPos = nodePositions[edge.target] || { x: 400, y: 400 };
                return (
                  <g key={edge.id || `${edge.source}-${edge.target}`}>
                    <line
                      x1={sourcePos.x}
                      y1={sourcePos.y}
                      x2={targetPos.x}
                      y2={targetPos.y}
                      stroke="#334155"
                      strokeWidth="2"
                      strokeDasharray={edge.relationship === 'GROUNDED_IN' ? '4 4' : 'none'}
                      markerEnd="url(#arrow)"
                    />
                    <text
                      x={(sourcePos.x + targetPos.x) / 2}
                      y={(sourcePos.y + targetPos.y) / 2 - 6}
                      fill="#64748B"
                      fontSize="9"
                      fontFamily="monospace"
                      textAnchor="middle"
                      className="bg-slate-900/80 px-1 py-0.5 rounded"
                    >
                      {edge.relationship}
                    </text>
                  </g>
                );
              })}
            </svg>

            <div 
              className="w-full h-full absolute inset-0 pointer-events-auto transition-transform duration-75"
              style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center center' }}
            >
              {visibleNodes.map((node) => {
                const pos = nodePositions[node.id] || { x: 300, y: 300 };
                const conf = NODE_CONFIG[node.type] || NODE_CONFIG.QUERY;
                const IconComponent = conf.icon;
                const isSelected = selectedNode?.id === node.id;

                return (
                  <div
                    key={node.id}
                    onMouseDown={(e) => handleMouseDownNode(e, node.id)}
                    onClick={() => setSelectedNode(node)}
                    style={{
                      left: `${pos.x}px`,
                      top: `${pos.y}px`,
                      transform: 'translate(-50%, -50%)',
                      borderColor: isSelected ? '#38BDF8' : conf.border,
                      boxShadow: isSelected ? `0 0 20px ${conf.color}80` : `0 4px 14px rgba(0,0,0,0.4)`
                    }}
                    className={`absolute cursor-grab active:cursor-grabbing px-3.5 py-2 rounded-xl bg-slate-900/90 border-2 backdrop-blur-md flex items-center space-x-2.5 transition-all hover:scale-105 ${
                      isSelected ? 'ring-2 ring-sky-400 z-30' : 'z-20'
                    }`}
                  >
                    <div 
                      className="p-1.5 rounded-lg flex items-center justify-center text-white"
                      style={{ backgroundColor: conf.color }}
                    >
                      <IconComponent className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-slate-100 whitespace-nowrap">
                        {node.label}
                      </div>
                      <div className="text-[9px] font-mono text-slate-400 uppercase tracking-wider">
                        {conf.label}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="absolute top-4 left-4 z-40 flex flex-wrap gap-1.5 max-w-xl bg-slate-900/80 p-2 rounded-xl border border-slate-800/80 backdrop-blur-md">
              <div className="flex items-center space-x-1 px-2 text-xs font-semibold text-slate-400 mr-1">
                <Filter className="w-3.5 h-3.5" />
                <span>Filter Nodes:</span>
              </div>
              {Object.entries(NODE_CONFIG).map(([type, cfg]) => {
                const isActive = activeFilters[type];
                return (
                  <button
                    key={type}
                    onClick={() => toggleFilter(type)}
                    style={{
                      backgroundColor: isActive ? `${cfg.color}25` : 'transparent',
                      borderColor: isActive ? cfg.color : '#334155',
                      color: isActive ? cfg.border : '#64748B'
                    }}
                    className="px-2.5 py-1 rounded-lg border text-[11px] font-medium transition-all"
                  >
                    {cfg.label}
                  </button>
                );
              })}
            </div>

            <div className="absolute bottom-4 left-4 z-40 bg-slate-900/80 border border-slate-800 p-3 rounded-xl backdrop-blur-md text-xs space-y-1 font-mono text-slate-300">
              <div className="flex items-center space-x-2 text-indigo-400 font-bold">
                <Network className="w-3.5 h-3.5" />
                <span>Topology Stats</span>
              </div>
              <div>Nodes: <span className="text-white">{visibleNodes.length}</span></div>
              <div>Edges: <span className="text-white">{visibleEdges.length}</span></div>
              <div>Density: <span className="text-emerald-400">{graphData?.stats?.density || '0.190'}</span></div>
            </div>
          </div>

          {selectedNode && (
            <div className="w-80 border-l border-slate-800 bg-slate-900/95 p-5 flex flex-col overflow-y-auto animate-in slide-in-from-right duration-200">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center space-x-2">
                  <Info className="w-4 h-4 text-indigo-400" />
                  <h4 className="text-sm font-bold text-white">Node Inspector</h4>
                </div>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="p-1 text-slate-400 hover:text-white rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-4 space-y-4 text-xs">
                <div>
                  <span className="text-slate-400 font-mono uppercase text-[10px]">Node ID</span>
                  <div className="p-2 mt-1 rounded bg-slate-950 border border-slate-800 font-mono text-indigo-300 break-all">
                    {selectedNode.id}
                  </div>
                </div>

                <div>
                  <span className="text-slate-400 font-mono uppercase text-[10px]">Node Type</span>
                  <div className="mt-1">
                    <span 
                      className="px-2 py-0.5 rounded text-[11px] font-bold text-white uppercase tracking-wider"
                      style={{ backgroundColor: selectedNode.color }}
                    >
                      {selectedNode.type}
                    </span>
                  </div>
                </div>

                <div>
                  <span className="text-slate-400 font-mono uppercase text-[10px]">Label</span>
                  <p className="mt-1 text-slate-200 font-medium">
                    {selectedNode.label}
                  </p>
                </div>

                <div>
                  <span className="text-slate-400 font-mono uppercase text-[10px]">Metadata Properties</span>
                  <pre className="mt-1 p-2.5 rounded bg-slate-950 border border-slate-800 text-slate-300 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap">
                    {JSON.stringify(selectedNode.metadata, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
