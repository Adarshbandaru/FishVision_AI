import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Microscope,
  BookOpen,
  Download,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
  Layers,
  ChevronRight,
  Trophy,
} from 'lucide-react';
import { api } from '../services/api';
import type { BenchmarksResponse, SampleSpecimen } from '../types';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [benchmarks, setBenchmarks] = useState<BenchmarksResponse | null>(null);
  const [samples, setSamples] = useState<SampleSpecimen[]>([]);

  useEffect(() => {
    api.getBenchmarks().then(setBenchmarks).catch(console.error);
    api.getSamplesManifest().then((s) => setSamples(s.slice(0, 8))).catch(console.error);
  }, []);

  const handleDownloadCSV = () => {
    if (!benchmarks) return;
    const headers = 'Model,Accuracy,Macro_Precision,Macro_Recall,Macro_F1,Weighted_F1\n';
    const rows = benchmarks.metrics
      .map(
        (m) =>
          `"${m.model}",${m.accuracy},${m.macro_precision},${m.macro_recall},${m.macro_f1},${m.weighted_f1 || 'N/A'}`
      )
      .join('\n');
    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'fishvision_model_benchmarks.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-8 animate-fadeIn">
      {/* 1. HERO HEADER BANNER */}
      <section className="relative rounded-2xl bg-surface-low border border-surface-highest/80 p-6 lg:p-8 overflow-hidden shadow-2xl">
        <div className="absolute -right-20 -bottom-20 w-96 h-96 rounded-full bg-primary/10 blur-[100px] pointer-events-none" />
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-8 relative z-10">
          <div className="flex flex-col max-w-3xl space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono text-primary uppercase tracking-wider bg-surface-container border border-primary/20 px-3 py-1 rounded-full flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-secondary shadow-[0_0_8px_rgba(71,239,214,0.8)] animate-pulse" />
                Ensemble Telemetry Ready
              </span>
              <span className="text-xs font-mono text-muted">// SYS_VER: 2.4.9_PROD</span>
            </div>

            <h1 className="text-3xl lg:text-4xl font-extrabold text-white tracking-tight">
              FishVision AI: Intelligent Species Recognition Platform
            </h1>
            <p className="text-base text-muted max-w-2xl leading-relaxed">
              Academic multi-model ensemble neural framework benchmarked across 152 distinct marine &
              freshwater taxa with zero-shot generalization capabilities.
            </p>

            {/* Action CTAs */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={() => navigate('/workspace')}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-primary text-background text-sm font-bold shadow-lg glow-cyan hover:bg-primary-light transition-all"
              >
                <Microscope className="w-4 h-4" />
                <span>Launch Recognition Workspace</span>
              </button>

              <button
                onClick={() => navigate('/catalog')}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-surface-container hover:bg-surface-high border border-surface-highest text-sm text-on-surface hover:text-primary transition-all"
              >
                <BookOpen className="w-4 h-4" />
                <span>Explore 152 Species Catalog</span>
              </button>

              <button
                onClick={handleDownloadCSV}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-surface-lowest/80 hover:bg-surface-container border border-surface-highest text-xs text-muted hover:text-white transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Download Evaluation Benchmark (CSV)</span>
              </button>
            </div>
          </div>

          {/* System Pill Telemetry Cards */}
          <div className="grid grid-cols-2 gap-3 min-w-[280px]">
            <div className="p-3.5 bg-surface-container/70 border border-surface-highest rounded-xl flex flex-col">
              <span className="text-[10px] font-mono text-muted uppercase">Indexed Taxa</span>
              <span className="text-2xl font-bold text-primary font-mono mt-0.5">152</span>
              <span className="text-[11px] text-secondary mt-0.5">100% taxonomic coverage</span>
            </div>

            <div className="p-3.5 bg-surface-container/70 border border-surface-highest rounded-xl flex flex-col">
              <span className="text-[10px] font-mono text-muted uppercase">SOTA Backbones</span>
              <span className="text-2xl font-bold text-primary font-mono mt-0.5">5 Models</span>
              <span className="text-[11px] text-primary/80 mt-0.5">Ensemble consensus</span>
            </div>

            <div className="p-3.5 bg-surface-container/70 border border-surface-highest rounded-xl flex flex-col">
              <span className="text-[10px] font-mono text-muted uppercase">Dataset Size</span>
              <span className="text-2xl font-bold text-primary font-mono mt-0.5">22,741</span>
              <span className="text-[11px] text-muted mt-0.5">Curated specimens</span>
            </div>

            <div className="p-3.5 bg-surface-container/70 border border-surface-highest rounded-xl flex flex-col">
              <span className="text-[10px] font-mono text-muted uppercase">Top-1 Accuracy</span>
              <span className="text-2xl font-bold text-secondary font-mono mt-0.5">93.90%</span>
              <span className="text-[11px] text-secondary mt-0.5">DINOv2 SOTA Peak</span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. KEY METRICS GRID */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1 */}
        <div className="p-5 rounded-2xl bg-surface-low border border-surface-highest/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono text-muted uppercase">MTRX_01 // TAXONOMY</span>
            <Layers className="w-4 h-4 text-primary" />
          </div>
          <div className="my-3">
            <div className="text-xs text-muted">Total Species Classified</div>
            <div className="text-3xl font-bold text-white font-mono mt-0.5">
              152 <span className="text-xs font-normal text-muted">taxa</span>
            </div>
          </div>
          <div className="space-y-1.5 pt-2 border-t border-surface-highest">
            <div className="flex justify-between text-[11px]">
              <span className="text-muted">Marine / Coastal</span>
              <span className="text-secondary font-mono">65%</span>
            </div>
            <div className="h-1 bg-surface-highest rounded-full overflow-hidden">
              <div className="h-full bg-secondary rounded-full" style={{ width: '65%' }} />
            </div>
            <div className="flex justify-between text-[11px] pt-1">
              <span className="text-muted">Freshwater / Riverine</span>
              <span className="text-primary font-mono">35%</span>
            </div>
            <div className="h-1 bg-surface-highest rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full" style={{ width: '35%' }} />
            </div>
          </div>
        </div>

        {/* Card 2 */}
        <div className="p-5 rounded-2xl bg-surface-low border border-surface-highest/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono text-muted uppercase">MTRX_02 // ACCURACY</span>
            <ShieldCheck className="w-4 h-4 text-secondary" />
          </div>
          <div className="my-3">
            <div className="text-xs text-muted">Top-1 Peak Accuracy</div>
            <div className="text-3xl font-bold text-secondary font-mono mt-0.5">93.90%</div>
          </div>
          <div className="text-xs text-muted leading-relaxed pt-2 border-t border-surface-highest">
            Achieved by <strong className="text-white">DINOv2</strong> (Vision Transformer with Register
            Tokens) on 3,309 held-out test specimens.
          </div>
        </div>

        {/* Card 3 */}
        <div className="p-5 rounded-2xl bg-surface-low border border-surface-highest/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono text-muted uppercase">MTRX_03 // ENSEMBLE</span>
            <Zap className="w-4 h-4 text-primary" />
          </div>
          <div className="my-3">
            <div className="text-xs text-muted">Architectural Paradigms</div>
            <div className="text-3xl font-bold text-white font-mono mt-0.5">3 Families</div>
          </div>
          <div className="text-xs text-muted leading-relaxed pt-2 border-t border-surface-highest">
            Combines Self-Supervised ViT, Windowed Swin Transformers, and Modern ConvNets for
            resilient consensus.
          </div>
        </div>

        {/* Card 4 */}
        <div className="p-5 rounded-2xl bg-surface-low border border-surface-highest/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono text-muted uppercase">MTRX_04 // INTERACTIVE</span>
            <Trophy className="w-4 h-4 text-yellow-400" />
          </div>
          <div className="my-3">
            <div className="text-xs text-muted">Authentic Sample Testing</div>
            <div className="text-3xl font-bold text-primary font-mono mt-0.5">Instant</div>
          </div>
          <div className="pt-2 border-t border-surface-highest flex items-center justify-between">
            <span className="text-xs text-muted">Test samples directly</span>
            <button
              onClick={() => navigate('/workspace')}
              className="text-xs text-secondary font-bold hover:underline flex items-center gap-1"
            >
              Try now <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </section>

      {/* 3. 5-MODEL BENCHMARK SHOWCASE */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              Fine-Tuned Neural Backbones Performance
            </h2>
            <p className="text-xs text-muted">
              Frozen test set evaluation across all 152 classes (3,309 held-out images).
            </p>
          </div>
          <button
            onClick={() => navigate('/benchmarks')}
            className="text-xs text-primary font-mono hover:underline flex items-center gap-1"
          >
            Full Benchmark Matrix <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {benchmarks?.metrics.map((m) => (
            <div
              key={m.model}
              className={`p-4 rounded-xl border transition-all ${
                m.model === 'DINOv2'
                  ? 'bg-surface-low border-primary/50 shadow-lg shadow-primary/10'
                  : 'bg-surface-low/70 border-surface-highest hover:border-surface-high'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono font-bold text-white">{m.model}</span>
                {m.model === 'DINOv2' && (
                  <span className="text-[9px] font-mono uppercase bg-primary text-background px-1.5 py-0.5 rounded font-bold">
                    SOTA
                  </span>
                )}
              </div>
              <div className="text-2xl font-bold font-mono text-secondary">
                {m.accuracy.toFixed(2)}%
              </div>
              <div className="text-[11px] text-muted mt-1">Accuracy</div>
              <div className="mt-3 pt-2 border-t border-surface-highest/60 space-y-1 text-[10px] font-mono">
                <div className="flex justify-between text-muted">
                  <span>Macro F1:</span>
                  <span className="text-on-surface">{m.macro_f1.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between text-muted">
                  <span>Precision:</span>
                  <span className="text-on-surface">{m.macro_precision.toFixed(2)}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. QUICK AUTHENTIC SPECIMEN SAMPLES STRIP */}
      {samples.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" />
              <h2 className="text-lg font-bold text-white">Quick Test Authentic Specimens</h2>
            </div>
            <button
              onClick={() => navigate('/catalog')}
              className="text-xs text-secondary font-mono hover:underline flex items-center gap-1"
            >
              View all 152 in Catalog <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
            {samples.map((s) => (
              <div
                key={s.id}
                onClick={() => navigate('/workspace', { state: { selectedSample: s } })}
                className="group p-2 rounded-xl bg-surface-low border border-surface-highest hover:border-primary/50 cursor-pointer transition-all hover:-translate-y-1"
              >
                <div className="aspect-square rounded-lg overflow-hidden bg-black/40 mb-2">
                  <img
                    src={api.getSampleImageUrl(s.filename)}
                    alt={s.common_name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                    loading="lazy"
                  />
                </div>
                <div className="text-[11px] font-bold text-on-surface truncate group-hover:text-primary">
                  {s.common_name}
                </div>
                <div className="text-[10px] font-mono text-muted truncate">{s.class_name}</div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
