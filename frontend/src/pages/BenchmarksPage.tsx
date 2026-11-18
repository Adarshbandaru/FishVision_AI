import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Gauge, Download, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';
import type { BenchmarksResponse } from '../types';

export const BenchmarksPage: React.FC = () => {
  const [benchmarks, setBenchmarks] = useState<BenchmarksResponse | null>(null);

  useEffect(() => {
    api
      .getBenchmarks()
      .then(setBenchmarks)
      .catch(console.error);
  }, []);

  const chartData =
    benchmarks?.metrics.map((m) => ({
      name: m.model,
      accuracy: m.accuracy,
      macroF1: m.macro_f1,
      macroPrecision: m.macro_precision,
      macroRecall: m.macro_recall,
    })) || [];

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

  const modelSpecs: Record<string, { params: string; inputSize: string; family: string }> = {
    DINOv2: { params: '86M', inputSize: '518x518', family: 'Self-Supervised Vision Transformer' },
    'ViT-B/16': { params: '86M', inputSize: '224x224', family: 'Vision Transformer' },
    'ConvNeXt Tiny': { params: '28M', inputSize: '224x224', family: 'Convolutional Neural Network' },
    'Swin Tiny': { params: '28M', inputSize: '224x224', family: 'Hierarchical Shifted-Window ViT' },
    MobileNetV3: { params: '5.4M', inputSize: '224x224', family: 'Efficient Convolutional Neural Network' },
  };

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface-low border border-surface-highest p-5 rounded-2xl">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <Gauge className="w-6 h-6 text-primary" />
            Model Comparison & Benchmark Matrix
          </h1>
          <p className="text-xs text-muted mt-0.5">
            Frozen evaluation metrics across 5 neural architectures benchmarked on 3,309 held-out test frames.
          </p>
        </div>

        <button
          onClick={handleDownloadCSV}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-surface-container hover:bg-surface-high border border-surface-highest text-xs text-primary font-bold transition-all shadow-sm"
        >
          <Download className="w-4 h-4" />
          <span>Export Metrics (CSV)</span>
        </button>
      </div>

      {/* Dataset Partitioning Telemetry */}
      {benchmarks?.dataset && (
        <section className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="p-4 rounded-xl bg-surface-low border border-surface-highest">
            <div className="text-[10px] font-mono text-muted uppercase">Taxonomic Classes</div>
            <div className="text-2xl font-bold text-white font-mono mt-1">
              {benchmarks.dataset.classes}
            </div>
            <div className="text-[10px] text-secondary mt-0.5">Verified distinct taxa</div>
          </div>

          <div className="p-4 rounded-xl bg-surface-low border border-surface-highest">
            <div className="text-[10px] font-mono text-muted uppercase">Training Split</div>
            <div className="text-2xl font-bold text-primary font-mono mt-1">
              {benchmarks.dataset.train.toLocaleString()}
            </div>
            <div className="text-[10px] text-muted mt-0.5">67.3% partition</div>
          </div>

          <div className="p-4 rounded-xl bg-surface-low border border-surface-highest">
            <div className="text-[10px] font-mono text-muted uppercase">Validation Split</div>
            <div className="text-2xl font-bold text-primary font-mono mt-1">
              {benchmarks.dataset.validation.toLocaleString()}
            </div>
            <div className="text-[10px] text-muted mt-0.5">18.1% partition</div>
          </div>

          <div className="p-4 rounded-xl bg-surface-low border border-surface-highest">
            <div className="text-[10px] font-mono text-secondary uppercase">Held-Out Test Split</div>
            <div className="text-2xl font-bold text-secondary font-mono mt-1">
              {benchmarks.dataset.test.toLocaleString()}
            </div>
            <div className="text-[10px] text-secondary mt-0.5">14.5% frozen test</div>
          </div>

          <div className="p-4 rounded-xl bg-surface-low border border-surface-highest col-span-2 md:col-span-1">
            <div className="text-[10px] font-mono text-muted uppercase">Total Dataset</div>
            <div className="text-2xl font-bold text-white font-mono mt-1">
              {benchmarks.dataset.total.toLocaleString()}
            </div>
            <div className="text-[10px] text-muted mt-0.5">Annotated specimens</div>
          </div>
        </section>
      )}

      {/* Visual Charts Grid */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Top-1 Accuracy Chart (7 cols) */}
        <div className="lg:col-span-7 p-5 rounded-2xl bg-surface-low border border-surface-highest space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                Top-1 Accuracy by Architecture (%)
              </h3>
              <p className="text-xs text-muted">Evaluated on the 3,309 held-out test split</p>
            </div>
            <span className="text-xs font-mono text-secondary">Higher is better</span>
          </div>

          <div className="h-72 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#222a3a" vertical={false} />
                <XAxis
                  dataKey="name"
                  stroke="#849495"
                  fontSize={11}
                  tickLine={false}
                  interval={0}
                />
                <YAxis stroke="#849495" fontSize={11} domain={[50, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#141c2b',
                    borderColor: '#2d3545',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: '#fff',
                  }}
                  formatter={(val: any) => [`${Number(val).toFixed(2)}%`, 'Accuracy']}
                />
                <Bar dataKey="accuracy" radius={[6, 6, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.name === 'DINOv2' ? '#00f2fe' : '#47efd6'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Macro F1 & Precision Comparison (5 cols) */}
        <div className="lg:col-span-5 p-5 rounded-2xl bg-surface-low border border-surface-highest space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Macro F1 Score by Architecture (%)
            </h3>
            <p className="text-xs text-muted">Unweighted average across all 152 classes</p>
          </div>

          <div className="h-72 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 10, right: 20, left: 10, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#222a3a" horizontal={false} />
                <XAxis type="number" stroke="#849495" fontSize={11} domain={[50, 100]} />
                <YAxis
                  dataKey="name"
                  type="category"
                  stroke="#849495"
                  fontSize={11}
                  tickLine={false}
                  width={90}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#141c2b',
                    borderColor: '#2d3545',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: '#fff',
                  }}
                  formatter={(val: any) => [`${Number(val).toFixed(2)}%`, 'Macro F1']}
                />
                <Bar dataKey="macroF1" fill="#00dce6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Verified Metrics Table */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-secondary" />
            Verified Test Set Metrics Matrix
          </h2>
          <p className="text-xs text-muted">
            Directly sourced from the final experiment evaluation protocol.
          </p>
        </div>

        <div className="overflow-x-auto rounded-2xl border border-surface-highest bg-surface-low">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-surface-highest bg-surface-container/50 font-mono text-[11px] text-muted uppercase">
                <th className="p-3.5 pl-5">Architecture</th>
                <th className="p-3.5">Family</th>
                <th className="p-3.5">Params</th>
                <th className="p-3.5">Input Res</th>
                <th className="p-3.5 font-bold text-secondary">Top-1 Accuracy</th>
                <th className="p-3.5">Macro Precision</th>
                <th className="p-3.5">Macro Recall</th>
                <th className="p-3.5">Macro F1</th>
                <th className="p-3.5 pr-5">Weighted F1</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-highest font-mono">
              {benchmarks?.metrics.map((m) => {
                const spec = modelSpecs[m.model] || {
                  params: 'N/A',
                  inputSize: '224x224',
                  family: 'CNN',
                };
                const isSOTA = m.model === 'DINOv2';
                return (
                  <tr
                    key={m.model}
                    className={`hover:bg-surface-container/40 transition-colors ${
                      isSOTA ? 'bg-primary/5 font-semibold' : ''
                    }`}
                  >
                    <td className="p-3.5 pl-5 text-white flex items-center gap-2 font-sans font-bold">
                      {m.model}
                      {isSOTA && (
                        <span className="text-[9px] font-mono uppercase bg-primary text-background px-1.5 py-0.5 rounded">
                          Peak
                        </span>
                      )}
                    </td>
                    <td className="p-3.5 text-muted font-sans">{spec.family}</td>
                    <td className="p-3.5 text-muted">{spec.params}</td>
                    <td className="p-3.5 text-muted">{spec.inputSize}</td>
                    <td className="p-3.5 text-secondary font-bold text-sm">
                      {m.accuracy.toFixed(2)}%
                    </td>
                    <td className="p-3.5 text-on-surface">{m.macro_precision.toFixed(2)}%</td>
                    <td className="p-3.5 text-on-surface">{m.macro_recall.toFixed(2)}%</td>
                    <td className="p-3.5 text-on-surface">{m.macro_f1.toFixed(2)}%</td>
                    <td className="p-3.5 pr-5 text-muted">
                      {m.weighted_f1 ? `${m.weighted_f1.toFixed(2)}%` : '—'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};
