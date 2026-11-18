import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Upload,
  Sparkles,
  Shuffle,
  AlertTriangle,
  CheckCircle2,
  Scan,
  Trash2,
  Play,
  Layers,
  ChevronDown,
  Info,
  Clock,
  Zap,
  Split,
  BarChart3,
  Check,
  X,
} from 'lucide-react';
import { api } from '../services/api';
import { historyStore } from '../utils/historyStore';
import type {
  PredictionResponse,
  SpeciesMetadata,
  SampleSpecimen,
  DetectionBox,
  SegmentationResult,
} from '../types';

export const WorkspacePage: React.FC = () => {
  const location = useLocation();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Input states
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [filename, setFilename] = useState<string>('Uploaded Specimen');

  // Sampling dropdown
  const [classList, setClassList] = useState<string[]>([]);
  const [selectedSpeciesFilter, setSelectedSpeciesFilter] = useState<string>('');
  const [samplingLoading, setSamplingLoading] = useState(false);

  // CV Mode toggles (strictly CPU Adaptive Saliency; YOLO/SAM documented as planned)
  const [cvMode, setCvMode] = useState<'standard' | 'crop_analyze' | 'segment'>('standard');
  const [detectionBox, setDetectionBox] = useState<DetectionBox | null>(null);
  const [segmentation, setSegmentation] = useState<SegmentationResult | null>(null);

  // Analysis states
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [speciesInfo, setSpeciesInfo] = useState<SpeciesMetadata | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [inferenceTimeMs, setInferenceTimeMs] = useState<number | null>(null);

  // Results View Toggle: 'diagnosis' | 'comparison_experiment'
  const [activeResultTab, setActiveResultTab] = useState<'diagnosis' | 'comparison_experiment'>(
    'diagnosis'
  );

  // Load class list on mount
  useEffect(() => {
    api.getClasses().then(setClassList).catch(console.error);
  }, []);

  // Handle incoming sample from route state (e.g. from Catalog or Gallery)
  useEffect(() => {
    const passedSample = (location.state as { selectedSample?: SampleSpecimen })?.selectedSample;
    if (passedSample) {
      loadSampleIntoWorkspace(passedSample);
    }
  }, [location.state]);

  const loadSampleIntoWorkspace = async (sample: SampleSpecimen) => {
    try {
      setSamplingLoading(true);
      setError(null);
      setPrediction(null);
      setDetectionBox(null);
      setSegmentation(null);

      const file = await api.fetchSampleImageFile(sample.filename);
      setSelectedFile(file);
      setFilename(sample.filename);
      setImagePreview(api.getSampleImageUrl(sample.filename));
    } catch (err: any) {
      setError(`Failed to load specimen sample: ${err.message || err}`);
    } finally {
      setSamplingLoading(false);
    }
  };

  const handleRandomDraw = async (filterSpecies?: string) => {
    try {
      setSamplingLoading(true);
      setError(null);
      const sample = await api.getRandomSample(filterSpecies || undefined);
      await loadSampleIntoWorkspace(sample);
    } catch (err: any) {
      setError(`Failed to draw random sample: ${err.message || err}`);
      setSamplingLoading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 15 * 1024 * 1024) {
      setError('File size exceeds the 15 MB threshold. Please upload a smaller image.');
      return;
    }

    setError(null);
    setPrediction(null);
    setDetectionBox(null);
    setSegmentation(null);
    setSelectedFile(file);
    setFilename(file.name);

    const reader = new FileReader();
    reader.onload = () => setImagePreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const handleRunInference = async () => {
    if (!selectedFile) {
      setError('Please upload an image or select a sample specimen first.');
      return;
    }

    setLoading(true);
    setError(null);
    const startTime = performance.now();

    try {
      let predRes: PredictionResponse;

      if (cvMode === 'crop_analyze') {
        const combined = await api.analyzeCombined(selectedFile);
        predRes = {
          results: combined.results,
          best_model: combined.best_model,
          consensus: combined.consensus,
          note: combined.pipeline,
        };
        setDetectionBox(combined.detection);
      } else {
        predRes = await api.predictImage(selectedFile);
        if (cvMode === 'segment') {
          const segRes = await api.segmentFishMask(selectedFile);
          setSegmentation(segRes);
          setDetectionBox(segRes.primary_roi);
        }
      }

      setPrediction(predRes);
      setInferenceTimeMs(Math.round(performance.now() - startTime));

      // Fetch ecological species metadata for the consensus / top prediction
      const primarySpecies = predRes.consensus.species || predRes.results[0].prediction;
      try {
        const meta = await api.getSpeciesByName(primarySpecies);
        setSpeciesInfo(meta);

        // Record to History Store
        if (imagePreview) {
          historyStore.addEntry(
            filename,
            imagePreview,
            meta.common_name || primarySpecies,
            meta.scientific_name || primarySpecies,
            predRes.results,
            predRes.consensus.agreement_count,
            predRes.consensus.total_models
          );
        }
      } catch {
        setSpeciesInfo(null);
      }
    } catch (err: any) {
      setError(`Inference failed: ${err.response?.data?.detail || err.message || err}`);
    } finally {
      setLoading(false);
    }
  };

  const clearWorkspace = () => {
    setSelectedFile(null);
    setImagePreview(null);
    setPrediction(null);
    setSpeciesInfo(null);
    setDetectionBox(null);
    setSegmentation(null);
    setError(null);
    setInferenceTimeMs(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const agreementCount = prediction?.consensus.agreement_count || 0;
  const totalModels = prediction?.consensus.total_models || 5;
  const isUnanimous = agreementCount === 5;
  const isHighAgreement = agreementCount >= 4;

  const modelSpecs: Record<string, { family: string; params: string; res: string }> = {
    DINOv2: { family: 'Self-Supervised Vision Transformer', params: '86M', res: '518x518' },
    'ViT-B/16': { family: 'Vision Transformer', params: '86M', res: '224x224' },
    'ConvNeXt Tiny': { family: 'Convolutional Neural Network', params: '28M', res: '224x224' },
    'Swin Tiny': { family: 'Hierarchical Shifted-Window ViT', params: '28M', res: '224x224' },
    MobileNetV3: { family: 'Efficient Convolutional Neural Network', params: '5.4M', res: '224x224' },
  };

  // Find maximum latency for comparative progress bar scaling
  const maxLatency = Math.max(
    ...(prediction?.results.map((r) => r.latency_ms || 10) || [100]),
    1
  );

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6 animate-fadeIn">
      {/* 1. WORKSPACE HEADER & CONTROL BAR */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface-low border border-surface-highest p-5 rounded-2xl">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <Scan className="w-6 h-6 text-primary" />
            Fish Recognition Workspace
          </h1>
          <p className="text-xs text-muted mt-0.5">
            Multi-model neural inference & taxonomic classification across 152 fish taxa.
          </p>
        </div>

        {/* Sampling Tools */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Species-specific Sampler */}
          <div className="relative">
            <select
              value={selectedSpeciesFilter}
              onChange={(e) => {
                const val = e.target.value;
                setSelectedSpeciesFilter(val);
                if (val) handleRandomDraw(val);
              }}
              className="appearance-none bg-surface-container border border-surface-highest text-xs text-on-surface pl-3 pr-8 py-2 rounded-xl focus:outline-none focus:border-primary cursor-pointer max-w-[190px] truncate"
            >
              <option value="">Sample by Species (152)...</option>
              {classList.map((cls) => (
                <option key={cls} value={cls}>
                  {cls}
                </option>
              ))}
            </select>
            <ChevronDown className="w-3.5 h-3.5 absolute right-2.5 top-1/2 -translate-y-1/2 text-muted pointer-events-none" />
          </div>

          {/* Random Specimen Button */}
          <button
            onClick={() => handleRandomDraw()}
            disabled={samplingLoading}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-surface-container hover:bg-surface-high border border-surface-highest text-xs font-semibold text-secondary hover:text-white transition-all disabled:opacity-50"
          >
            <Shuffle className={`w-3.5 h-3.5 ${samplingLoading ? 'animate-spin' : ''}`} />
            <span>Surprise Me</span>
          </button>

          {/* Hidden File Input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp,image/bmp"
            onChange={handleFileUpload}
            className="hidden"
          />

          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary text-background text-xs font-bold hover:bg-primary-light transition-all shadow-md glow-cyan"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload Image</span>
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/50 border border-rose-500/80 text-rose-200 text-xs flex items-center justify-between animate-fadeIn">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="text-rose-400 hover:text-white">
            Dismiss
          </button>
        </div>
      )}

      {/* 2. MAIN WORKSPACE GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Image Canvas & Pipeline Settings (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="relative aspect-[4/3] rounded-2xl bg-surface-low border border-surface-highest overflow-hidden flex items-center justify-center group shadow-xl">
            {imagePreview ? (
              <div className="relative w-full h-full flex items-center justify-center bg-black/60">
                <img
                  src={imagePreview}
                  alt="Fish Specimen"
                  className="w-full h-full object-contain"
                />

                {/* Bounding Box Overlay if Detection Active */}
                {detectionBox && (
                  <div
                    className="absolute border-2 border-primary bg-primary/10 rounded pointer-events-none transition-all duration-300"
                    style={{
                      top: `${detectionBox.box_2d[0] * 100}%`,
                      left: `${detectionBox.box_2d[1] * 100}%`,
                      height: `${(detectionBox.box_2d[2] - detectionBox.box_2d[0]) * 100}%`,
                      width: `${(detectionBox.box_2d[3] - detectionBox.box_2d[1]) * 100}%`,
                    }}
                  >
                    <span className="absolute -top-6 left-0 bg-primary text-background font-mono text-[9px] font-bold px-1.5 py-0.5 rounded shadow">
                      {detectionBox.label} ({detectionBox.confidence}%)
                    </span>
                  </div>
                )}

                {/* Segmentation Polygon SVG Overlay */}
                {segmentation && (
                  <svg
                    className="absolute inset-0 w-full h-full pointer-events-none"
                    viewBox="0 0 100 100"
                    preserveAspectRatio="none"
                  >
                    <polygon
                      points={segmentation.polygon_normalized
                        .map(([x, y]) => `${x * 100},${y * 100}`)
                        .join(' ')}
                      fill="rgba(71, 239, 214, 0.2)"
                      stroke="#47efd6"
                      strokeWidth="0.8"
                      strokeDasharray="2,1"
                    />
                  </svg>
                )}

                <div className="absolute top-3 left-3 bg-black/70 backdrop-blur-sm px-2.5 py-1 rounded-lg text-[10px] font-mono text-secondary border border-surface-highest">
                  {filename}
                </div>

                <button
                  onClick={clearWorkspace}
                  className="absolute top-3 right-3 p-1.5 rounded-lg bg-black/70 hover:bg-rose-900/80 text-muted hover:text-white transition-colors"
                  title="Clear Specimen"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="flex flex-col items-center justify-center p-8 text-center cursor-pointer hover:bg-surface-high/30 transition-colors w-full h-full"
              >
                <div className="w-14 h-14 rounded-2xl bg-surface-container border border-surface-highest flex items-center justify-center text-primary mb-3 shadow-inner">
                  <Upload className="w-6 h-6 stroke-[1.8]" />
                </div>
                <div className="text-sm font-bold text-white mb-1">
                  Upload Fish Specimen Image
                </div>
                <p className="text-xs text-muted max-w-xs">
                  Drag & drop or click to upload. Supports JPG, PNG, WEBP up to 15 MB.
                </p>
                <div className="mt-4 flex items-center gap-2">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRandomDraw();
                    }}
                    className="text-xs font-mono text-secondary hover:underline flex items-center gap-1"
                  >
                    <Sparkles className="w-3.5 h-3.5" /> Or load random authentic sample
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Computer Vision Pipeline Selector */}
          <div className="p-4 rounded-xl bg-surface-low border border-surface-highest space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase tracking-wider text-muted flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-primary" /> Vision Pipeline Mode
              </span>
              <span className="text-[10px] font-mono text-secondary">CPU Safe</span>
            </div>

            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setCvMode('standard')}
                className={`p-2.5 rounded-xl border text-left transition-all ${
                  cvMode === 'standard'
                    ? 'bg-primary/10 border-primary text-white font-bold'
                    : 'bg-surface-container border-surface-highest text-muted hover:text-white'
                }`}
              >
                <div className="text-xs">Standard</div>
                <div className="text-[10px] text-muted font-normal mt-0.5">5-Model Ensemble</div>
              </button>

              <button
                type="button"
                onClick={() => setCvMode('crop_analyze')}
                className={`p-2.5 rounded-xl border text-left transition-all ${
                  cvMode === 'crop_analyze'
                    ? 'bg-primary/10 border-primary text-white font-bold'
                    : 'bg-surface-container border-surface-highest text-muted hover:text-white'
                }`}
              >
                <div className="text-xs">ROI Crop</div>
                <div className="text-[10px] text-muted font-normal mt-0.5">Adaptive Saliency</div>
              </button>

              <button
                type="button"
                onClick={() => setCvMode('segment')}
                className={`p-2.5 rounded-xl border text-left transition-all ${
                  cvMode === 'segment'
                    ? 'bg-primary/10 border-primary text-white font-bold'
                    : 'bg-surface-container border-surface-highest text-muted hover:text-white'
                }`}
              >
                <div className="text-xs">Contour Mask</div>
                <div className="text-[10px] text-muted font-normal mt-0.5">Adaptive Saliency</div>
              </button>
            </div>

            <p className="text-[10px] text-muted leading-tight">
              *Active pipeline runs on CPU Adaptive Saliency. YOLO26 detection & SAM segmentation
              are documented as planned neural extensions when verified weights are mounted.
            </p>

            {/* Run Analysis Action Button */}
            <button
              onClick={handleRunInference}
              disabled={loading || !selectedFile}
              className="w-full py-3 rounded-xl bg-primary text-background font-bold text-sm hover:bg-primary-light transition-all flex items-center justify-center gap-2 shadow-lg glow-cyan disabled:opacity-50 disabled:pointer-events-none mt-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-background border-t-transparent rounded-full animate-spin" />
                  <span>Evaluating 5 Neural Backbones...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Analyze Fish Specimen</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Prediction Results & Live Experiment (7 cols) */}
        <div className="lg:col-span-7 space-y-5">
          {prediction ? (
            <>
              {/* Tab Selector: Diagnosis vs Live Model Comparison Experiment */}
              <div className="flex items-center gap-2 p-1.5 bg-surface-low border border-surface-highest rounded-xl">
                <button
                  onClick={() => setActiveResultTab('diagnosis')}
                  className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                    activeResultTab === 'diagnosis'
                      ? 'bg-primary text-background shadow-md'
                      : 'text-muted hover:text-white'
                  }`}
                >
                  <Scan className="w-3.5 h-3.5" />
                  <span>Taxonomic Diagnosis</span>
                </button>

                <button
                  onClick={() => setActiveResultTab('comparison_experiment')}
                  className={`flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                    activeResultTab === 'comparison_experiment'
                      ? 'bg-primary text-background shadow-md'
                      : 'text-muted hover:text-white'
                  }`}
                >
                  <BarChart3 className="w-3.5 h-3.5" />
                  <span>Live Model Comparison Experiment</span>
                </button>
              </div>

              {/* Consensus Banner */}
              <div
                className={`p-4 rounded-2xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                  isUnanimous
                    ? 'bg-emerald-950/40 border-emerald-500/70 text-emerald-200'
                    : isHighAgreement
                    ? 'bg-cyan-950/40 border-cyan-500/70 text-cyan-200'
                    : 'bg-amber-950/40 border-amber-500/70 text-amber-200'
                }`}
              >
                <div className="flex items-center gap-3">
                  {isUnanimous ? (
                    <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
                  ) : isHighAgreement ? (
                    <CheckCircle2 className="w-6 h-6 text-cyan-400 shrink-0" />
                  ) : (
                    <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0" />
                  )}
                  <div>
                    <div className="text-sm font-bold flex items-center gap-2">
                      <span>
                        Ensemble Consensus: {agreementCount} of {totalModels} Models Agree
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-black/40">
                        {isUnanimous ? 'Unanimous' : isHighAgreement ? 'Strong Majority' : 'Split Verdict'}
                      </span>
                    </div>
                    <p className="text-xs opacity-90 mt-0.5">
                      {isUnanimous
                        ? 'All five architectures independently converged on this taxonomic class.'
                        : isHighAgreement
                        ? 'Four models agree on the primary classification.'
                        : 'Noticeable divergence among backbones. Softmax confidence is uncalibrated.'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 text-xs font-mono opacity-80 shrink-0">
                  {prediction.total_latency_ms ? (
                    <span className="flex items-center gap-1 text-primary">
                      <Zap className="w-3.5 h-3.5" />
                      <span>{prediction.total_latency_ms}ms total</span>
                    </span>
                  ) : inferenceTimeMs ? (
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{inferenceTimeMs}ms</span>
                    </span>
                  ) : null}
                </div>
              </div>

              {/* TAB 1: DIAGNOSIS & SPECIES METADATA */}
              {activeResultTab === 'diagnosis' ? (
                <>
                  {/* Primary Prediction Card */}
                  <div className="p-6 rounded-2xl bg-surface-low border border-primary/40 shadow-xl relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                      <div>
                        <div className="text-[10px] font-mono uppercase tracking-wider text-primary mb-1">
                          PRIMARY VERDICT // DINOv2 SOTA BACKBONE
                        </div>
                        <h2 className="text-3xl font-extrabold text-white tracking-tight">
                          {speciesInfo?.common_name || prediction.consensus.species}
                        </h2>
                        <div className="text-sm italic text-muted font-serif mt-0.5">
                          {speciesInfo?.scientific_name || prediction.consensus.species}
                        </div>
                      </div>

                      <div className="text-right sm:text-right">
                        <div className="text-[10px] font-mono text-muted uppercase">Confidence</div>
                        <div className="text-3xl font-bold font-mono text-secondary">
                          {prediction.results[0].confidence.toFixed(1)}%
                        </div>
                        <div className="text-[10px] font-mono text-muted/70">Raw Softmax</div>
                      </div>
                    </div>

                    {/* Top-5 Probability Bars */}
                    <div className="mt-6 pt-5 border-t border-surface-highest space-y-2.5">
                      <div className="text-xs font-mono uppercase tracking-wider text-muted">
                        Top-5 Ranked Class Candidates (DINOv2)
                      </div>
                      <div className="space-y-2">
                        {prediction.results[0].top5.map((c, i) => (
                          <div key={c.species} className="space-y-1">
                            <div className="flex justify-between text-xs">
                              <span className="text-on-surface font-medium truncate max-w-[280px]">
                                {i + 1}. {c.species}
                              </span>
                              <span className="font-mono text-secondary font-bold">
                                {c.confidence.toFixed(2)}%
                              </span>
                            </div>
                            <div className="w-full h-1.5 bg-surface-container rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full transition-all duration-500 ${
                                  i === 0 ? 'bg-primary' : 'bg-surface-highest'
                                }`}
                                style={{ width: `${Math.max(2, c.confidence)}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Species Ecological Details Card */}
                  {speciesInfo && (
                    <div className="p-5 rounded-2xl bg-surface-low border border-surface-highest space-y-4">
                      <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-primary">
                        <Info className="w-4 h-4" /> Comprehensive Taxon Ecological Profile
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                        <div>
                          <div className="text-muted font-mono uppercase text-[10px]">Water Type</div>
                          <div className="text-on-surface font-semibold mt-0.5">
                            {speciesInfo.water_type}
                          </div>
                        </div>

                        <div>
                          <div className="text-muted font-mono uppercase text-[10px]">Conservation</div>
                          <div className="text-on-surface font-semibold mt-0.5">
                            {speciesInfo.conservation_status}
                          </div>
                        </div>

                        <div>
                          <div className="text-muted font-mono uppercase text-[10px]">Typical Size</div>
                          <div className="text-on-surface font-semibold mt-0.5">
                            {speciesInfo.typical_size}
                          </div>
                        </div>

                        <div className="col-span-2 sm:col-span-3">
                          <div className="text-muted font-mono uppercase text-[10px]">Habitat & Range</div>
                          <div className="text-on-surface mt-0.5 leading-relaxed">
                            {speciesInfo.habitat}
                          </div>
                        </div>

                        <div className="col-span-2 sm:col-span-3">
                          <div className="text-muted font-mono uppercase text-[10px]">Diet & Trophic Level</div>
                          <div className="text-on-surface mt-0.5 leading-relaxed">
                            {speciesInfo.diet}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                /* TAB 2: LIVE MODEL COMPARISON EXPERIMENT */
                <div className="space-y-5 animate-fadeIn">
                  {/* Agreement vs Disagreements Panel */}
                  <div className="p-5 rounded-2xl bg-surface-low border border-surface-highest space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Split className="w-5 h-5 text-secondary" />
                        <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                          Live Agreement & Disagreement Breakdown
                        </h3>
                      </div>
                      <span className="text-xs font-mono text-primary font-bold">
                        {prediction.consensus.agreement_percentage || (agreementCount / 5) * 100}% Concordance
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                      {/* Agreeing Models */}
                      <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-500/40 space-y-2">
                        <div className="flex items-center gap-1.5 text-emerald-400 font-bold font-mono text-xs">
                          <Check className="w-4 h-4" /> Concurring Architectures ({agreementCount}/5)
                        </div>
                        <p className="text-[11px] text-emerald-200/80">
                          Agreed on predicted taxon: <strong>{prediction.consensus.species}</strong>
                        </p>
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {(prediction.consensus.agreeing_models || []).map((name) => (
                            <span
                              key={name}
                              className="px-2 py-0.5 rounded-full bg-emerald-900/60 border border-emerald-500/50 text-[10px] font-mono text-emerald-300 font-semibold"
                            >
                              {name}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Disagreeing Models */}
                      <div className="p-3.5 rounded-xl bg-amber-950/30 border border-amber-500/40 space-y-2">
                        <div className="flex items-center gap-1.5 text-amber-400 font-bold font-mono text-xs">
                          <X className="w-4 h-4" /> Divergent Interpretations ({5 - agreementCount}/5)
                        </div>
                        {prediction.consensus.disagreeing_models &&
                        prediction.consensus.disagreeing_models.length > 0 ? (
                          <div className="space-y-1.5 pt-1">
                            {prediction.consensus.disagreeing_models.map((dm) => (
                              <div
                                key={dm.model}
                                className="p-2 rounded-lg bg-black/40 border border-amber-500/30 flex items-center justify-between text-[11px]"
                              >
                                <div>
                                  <span className="font-bold text-amber-300">{dm.model}:</span>{' '}
                                  <span className="text-on-surface">{dm.predicted}</span>
                                </div>
                                <span className="font-mono text-amber-400 font-bold">
                                  {dm.confidence.toFixed(1)}%
                                </span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-[11px] text-muted leading-relaxed pt-1">
                            Zero architectural disagreements detected. All five neural backbones
                            independently arrived at the exact same taxonomic species.
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Inference Latency Benchmark Breakdown */}
                  <div className="p-5 rounded-2xl bg-surface-low border border-surface-highest space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Zap className="w-4 h-4 text-primary" />
                        <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                          Live Inference Latency Benchmark (ms)
                        </h3>
                      </div>
                      <span className="text-[11px] font-mono text-muted">CPU Execution Time</span>
                    </div>

                    <div className="space-y-2 pt-1">
                      {prediction.results.map((r) => {
                        const ms = r.latency_ms || 25;
                        const pct = Math.min(100, Math.max(10, (ms / maxLatency) * 100));
                        return (
                          <div key={r.model} className="space-y-1">
                            <div className="flex items-center justify-between text-xs">
                              <span className="font-mono text-white font-bold">{r.model}</span>
                              <div className="flex items-center gap-2">
                                <span className="text-[10px] text-muted">
                                  {modelSpecs[r.model]?.params} params
                                </span>
                                <span className="font-mono text-secondary font-bold">
                                  {ms.toFixed(1)} ms
                                </span>
                              </div>
                            </div>
                            <div className="w-full h-1.5 bg-surface-container rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-primary to-secondary rounded-full transition-all duration-500"
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* 5-Model Side-by-Side Architectural Interpretation Cards */}
                  <div className="space-y-3">
                    <div className="text-xs font-mono uppercase tracking-wider text-muted">
                      Full 5-Model Prediction Matrix & Top-3 Ranked Alternatives
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
                      {prediction.results.map((m) => {
                        const isMatch = m.prediction === prediction.consensus.species;
                        const spec = modelSpecs[m.model] || {
                          family: 'CNN',
                          params: 'N/A',
                          res: '224x224',
                        };

                        return (
                          <div
                            key={m.model}
                            className={`p-3.5 rounded-2xl border flex flex-col justify-between transition-all ${
                              isMatch
                                ? 'bg-surface-low border-surface-highest'
                                : 'bg-amber-950/20 border-amber-500/60 shadow-lg shadow-amber-950/20'
                            }`}
                          >
                            <div className="space-y-2">
                              {/* Header */}
                              <div className="flex items-center justify-between">
                                <span className="text-xs font-bold text-white font-mono">
                                  {m.model}
                                </span>
                                <span
                                  className={`text-[9px] font-mono font-bold px-1.5 py-0.2 rounded ${
                                    isMatch
                                      ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-500/40'
                                      : 'bg-amber-950/60 text-amber-300 border border-amber-500/40'
                                  }`}
                                >
                                  {isMatch ? 'Concordant' : 'Divergent'}
                                </span>
                              </div>

                              <div className="text-[10px] text-muted">{spec.family}</div>

                              {/* Prediction & Confidence */}
                              <div className="pt-1">
                                <div className="text-[10px] font-mono uppercase text-muted">
                                  Predicted Taxon
                                </div>
                                <div className="text-xs font-bold text-primary truncate mt-0.5">
                                  {m.prediction}
                                </div>
                                <div className="text-sm font-bold font-mono text-secondary mt-0.5">
                                  {m.confidence.toFixed(1)}%
                                </div>
                              </div>

                              {/* Top-3 Candidates Breakdown */}
                              <div className="pt-2 border-t border-surface-highest/60 space-y-1.5">
                                <div className="text-[9px] font-mono text-muted uppercase">
                                  Top-3 Alternatives
                                </div>
                                {m.top5.slice(0, 3).map((c, i) => (
                                  <div key={c.species} className="text-[10px] space-y-0.5">
                                    <div className="flex justify-between text-muted">
                                      <span className="truncate max-w-[80px]">
                                        {i + 1}. {c.species}
                                      </span>
                                      <span className="font-mono text-on-surface">
                                        {c.confidence.toFixed(1)}%
                                      </span>
                                    </div>
                                    <div className="w-full h-1 bg-surface-container rounded-full overflow-hidden">
                                      <div
                                        className={`h-full ${
                                          i === 0 ? 'bg-primary' : 'bg-surface-highest'
                                        }`}
                                        style={{ width: `${Math.max(2, c.confidence)}%` }}
                                      />
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>

                            {/* Measured Latency Footer */}
                            <div className="mt-3 pt-2 border-t border-surface-highest/60 flex items-center justify-between text-[10px] font-mono text-muted">
                              <span>Latency:</span>
                              <span className="text-secondary font-bold">
                                {m.latency_ms ? `${m.latency_ms} ms` : '~25 ms'}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="h-full min-h-[360px] rounded-2xl bg-surface-low/50 border border-dashed border-surface-highest flex flex-col items-center justify-center p-8 text-center text-muted">
              <Scan className="w-12 h-12 text-surface-highest mb-3" />
              <div className="text-sm font-bold text-white mb-1">Awaiting Specimen Analysis</div>
              <p className="text-xs text-muted max-w-sm">
                Upload a fish image or select a specimen to evaluate with DINOv2, ViT-B/16,
                ConvNeXt Tiny, Swin Tiny, and MobileNetV3 in our Live Model Comparison Experiment.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
