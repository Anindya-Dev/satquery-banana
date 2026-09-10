import React, { useState } from 'react';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import PartnersSection from './components/PartnersSection';
import HeroQueryCenter from './components/HeroQueryCenter';
import VisualCanvas from './components/VisualCanvas';
import EvidenceGroundingPanel from './components/EvidenceGroundingPanel';
import FeaturesSection from './components/FeaturesSection';
import DeepFeatureShowcase from './components/DeepFeatureShowcase';
import SolutionsAccordion from './components/SolutionsAccordion';
import MetricsBanner from './components/MetricsBanner';
import SIHComplianceChecklist from './components/SIHComplianceChecklist';
import FooterCTA from './components/FooterCTA';
import DemoScenariosModal from './components/DemoScenariosModal';
import { DEMO_SCENARIOS } from './data/demoScenarios';
import { Activity } from 'lucide-react';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export default function App() {
  const [activeScenario, setActiveScenario] = useState(DEMO_SCENARIOS[0]);
  const [currentTask, setCurrentTask] = useState(DEMO_SCENARIOS[0].task);
  const [queryText, setQueryText] = useState(DEMO_SCENARIOS[0].query);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);
  const [pipelineToast, setPipelineToast] = useState(null);
  const [analysisArea, setAnalysisArea] = useState({
    bbox: DEMO_SCENARIOS[0].bbox.join(','),
    startDate: '2024-05-01T00:00:00Z',
    endDate: '2024-05-31T23:59:59Z',
  });

  // Switch task mode & map to corresponding demo scenario if available
  const handleSelectTask = (taskMode) => {
    setCurrentTask(taskMode);
    const matchedScenario = DEMO_SCENARIOS.find(s => s.task === taskMode) || DEMO_SCENARIOS[0];
    setActiveScenario(matchedScenario);
    setQueryText(matchedScenario.query);

    // Scroll smoothly to platform section
    const elem = document.getElementById('platform');
    if (elem) elem.scrollIntoView({ behavior: 'smooth' });
  };

  // Switch active scenario directly
  const handleSelectScenario = (scenario) => {
    setActiveScenario(scenario);
    setCurrentTask(scenario.task);
    setQueryText(scenario.query);
  };

  const handleRunAnalysis = async () => {
    if (!API_BASE_URL) {
      setPipelineToast('API URL is not configured for this deployment.');
      return;
    }
    const bbox = analysisArea.bbox.split(',').map(Number);
    if (bbox.length !== 4 || bbox.some(Number.isNaN)) {
      setPipelineToast('Enter four valid AOI coordinates: min longitude, min latitude, max longitude, max latitude.');
      return;
    }
    setIsAnalyzing(true);
    setPipelineToast('Searching live satellite scenes...');
    const taskTypes = {
      SINGLE_IMAGE_VQA: 'Visual Question Answering',
      VISUAL_GROUNDING: 'Visual Grounding & Segmentation',
      CHANGE_DETECTION: 'Bi-Temporal Change Detection',
      OPTICAL_SAR_FUSION: 'Optical-SAR Multimodal Fusion',
      AGENTIC_ROUTING: 'Auto-Classified Query',
    };
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryText,
          task_type: taskTypes[currentTask],
          bbox,
          start_date: analysisArea.startDate,
          end_date: analysisArea.endDate,
        }),
      });
      const data = await response.json();
      if (!response.ok || data.refusal_triggered) throw new Error(data.refusal_reason || data.error?.message || 'Analysis could not be completed.');
      setActiveScenario((previous) => ({
        ...previous,
        bbox,
        imageType: data.image_secondary_url ? 'pair' : 'single',
        imagePrimary: data.image_primary_url || previous.imagePrimary,
        imageSecondary: data.image_secondary_url || previous.imageSecondary,
        groundedAnswer: data.summary_answer,
        confidence: {
          level: data.confidence.rating,
          score: Math.round(data.confidence.score * 100),
          factors: data.confidence.factors,
        },
        evidenceChain: data.evidence_chain.map((item) => ({ id: item.evidence_id, type: item.evidence_type, desc: item.description, source: item.layer, value: `${item.metric_name}: ${item.metric_value} ${item.unit}` })),
        spectralData: Object.fromEntries(Object.entries(data.spectral_indices || {}).filter(([, value]) => value !== null).map(([key, value]) => [key.toUpperCase().replace('_MEAN', ''), { avg: Number(value).toFixed(3) }])),
      }));
      setPipelineToast(`Live analysis complete in ${Math.round(data.processing_time_ms)} ms.`);
    } catch (error) {
      setPipelineToast(error.message);
    } finally {
      setIsAnalyzing(false);
      setTimeout(() => setPipelineToast(null), 6000);
    }
  };

  const scrollToPlatform = () => {
    const elem = document.getElementById('platform');
    if (elem) elem.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 relative selection:bg-orange-500/20 selection:text-orange-900">
      
      {/* Light Theme Floating Navbar */}
      <Navbar 
        onOpenDemoModal={() => setIsDemoModalOpen(true)}
        currentScenarioTitle={activeScenario?.title}
      />

      {/* Hackathon Hero Section */}
      <HeroSection 
        onOpenDemoModal={() => setIsDemoModalOpen(true)}
        onScrollToPlatform={scrollToPlatform}
      />

      {/* Earth Observation Constellations Banner */}
      <PartnersSection />

      {/* Interactive Platform Section (Embedded Live Engine Console) */}
      <section id="platform" className="py-12 border-t border-slate-200/80 relative bg-slate-100/60">
        <div className="text-center max-w-3xl mx-auto mb-8 px-6">
          <div className="section-tag">LIVE PROTOTYPE ENGINE</div>
          <h2 className="heading-font text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Interactive Remote Sensing Assistant Console
          </h2>
          <p className="mt-2 text-sm sm:text-base text-slate-600">
            Execute single-image queries, bi-temporal change detection, SAM grounding, and optical+SAR fusion.
          </p>
        </div>

        {/* Hero Query Command Center */}
        <HeroQueryCenter 
          currentTask={currentTask}
          onSelectTask={handleSelectTask}
          queryText={queryText}
          setQueryText={setQueryText}
          onRunAnalysis={handleRunAnalysis}
          isAnalyzing={isAnalyzing}
          activeScenario={activeScenario}
          analysisArea={analysisArea}
          setAnalysisArea={setAnalysisArea}
        />

        {/* Interactive Dual Viewport & Evidence Panel */}
        <div className="px-6 max-w-7xl w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6 mt-6">
          {/* Left: Visual Canvas */}
          <div className="lg:col-span-7 flex flex-col">
            <VisualCanvas scenario={activeScenario} />
          </div>

          {/* Right: Evidence & Grounding Panel */}
          <div className="lg:col-span-5 flex flex-col">
            <EvidenceGroundingPanel scenario={activeScenario} />
          </div>
        </div>
      </section>

      {/* SIH Official Problem Statement Requirements */}
      <FeaturesSection onSelectTask={handleSelectTask} />

      {/* System Architecture & Validation Gates */}
      <DeepFeatureShowcase onOpenDemoModal={() => setIsDemoModalOpen(true)} />

      {/* Supported Analysis Applications */}
      <SolutionsAccordion />

      {/* Deterministic Verification Metrics */}
      <MetricsBanner />

      {/* Official SIH Problem Statement Compliance Checklist */}
      <SIHComplianceChecklist />

      {/* Technical Footer & Action Banner */}
      <FooterCTA onOpenDemoModal={() => setIsDemoModalOpen(true)} />

      {/* Pipeline Status Toast Banner */}
      {pipelineToast && (
        <div className="fixed bottom-6 right-6 z-50 glass-panel-amber px-4 py-3 text-xs font-mono font-semibold text-orange-900 flex items-center gap-3 animate-bounce shadow-xl border border-orange-300 bg-orange-50">
          <Activity className="w-4 h-4 text-orange-600 animate-spin" />
          <span>{pipelineToast}</span>
        </div>
      )}

      {/* SIH Demo Suite Modal */}
      <DemoScenariosModal 
        isOpen={isDemoModalOpen}
        onClose={() => setIsDemoModalOpen(false)}
        onSelectScenario={handleSelectScenario}
        activeScenarioId={activeScenario?.id}
      />

    </div>
  );
}
