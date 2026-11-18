import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  History,
  Download,
  Trash2,
  Search,
  CheckCircle2,
  AlertTriangle,
  Microscope,
  Calendar,
} from 'lucide-react';
import { historyStore } from '../utils/historyStore';
import type { HistoryItem } from '../types';

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [search, setSearch] = useState('');
  const [filterAgreement, setFilterAgreement] = useState<'all' | 'unanimous' | 'disagreement'>(
    'all'
  );

  useEffect(() => {
    setHistory(historyStore.getHistory());
  }, []);

  const handleClear = () => {
    if (window.confirm('Are you sure you want to clear your local prediction history?')) {
      historyStore.clearHistory();
      setHistory([]);
    }
  };

  const handleExportJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(history, null, 2));
    const a = document.createElement('a');
    a.href = dataStr;
    a.download = `fishvision_history_${Date.now()}.json`;
    a.click();
  };

  const filtered = history.filter((item) => {
    const matchesSearch =
      item.predictedSpecies.toLowerCase().includes(search.toLowerCase()) ||
      item.scientificName.toLowerCase().includes(search.toLowerCase()) ||
      item.filename.toLowerCase().includes(search.toLowerCase());

    if (filterAgreement === 'unanimous') {
      return matchesSearch && item.agreementCount === item.totalModels;
    }
    if (filterAgreement === 'disagreement') {
      return matchesSearch && item.agreementCount < item.totalModels;
    }
    return matchesSearch;
  });

  const unanimousCount = history.filter((h) => h.agreementCount === h.totalModels).length;
  const unanimousPct =
    history.length > 0 ? Math.round((unanimousCount / history.length) * 100) : 0;

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface-low border border-surface-highest p-5 rounded-2xl">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <History className="w-6 h-6 text-primary" />
            Prediction History & Audit Log
          </h1>
          <p className="text-xs text-muted mt-0.5">
            Persistent audit trail of specimen inference, ensemble consensus, and cross-model agreement.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {history.length > 0 && (
            <>
              <button
                onClick={handleExportJSON}
                className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-surface-container hover:bg-surface-high border border-surface-highest text-xs text-primary font-bold transition-all"
              >
                <Download className="w-4 h-4" />
                <span>Export JSON</span>
              </button>

              <button
                onClick={handleClear}
                className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-surface-lowest hover:bg-rose-950/60 border border-surface-highest hover:border-rose-700/60 text-xs text-muted hover:text-rose-300 transition-all"
              >
                <Trash2 className="w-4 h-4" />
                <span>Clear</span>
              </button>
            </>
          )}

          <button
            onClick={() => navigate('/workspace')}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary text-background text-xs font-bold hover:bg-primary-light transition-all shadow-md glow-cyan"
          >
            <Microscope className="w-4 h-4" />
            <span>New Evaluation</span>
          </button>
        </div>
      </div>

      {/* Summary KPI Strip */}
      {history.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-surface-low border border-surface-highest">
            <div className="text-[10px] font-mono text-muted uppercase">Evaluated Specimens</div>
            <div className="text-2xl font-bold text-white font-mono mt-1">{history.length}</div>
            <div className="text-[10px] text-muted mt-0.5">Logged in local session</div>
          </div>

          <div className="p-4 rounded-xl bg-surface-low border border-surface-highest">
            <div className="text-[10px] font-mono text-muted uppercase">Unanimous Consensus</div>
            <div className="text-2xl font-bold text-secondary font-mono mt-1">
              {unanimousCount} ({unanimousPct}%)
            </div>
            <div className="text-[10px] text-secondary mt-0.5">5 of 5 models concordant</div>
          </div>

          <div className="p-4 rounded-xl bg-surface-low border border-surface-highest">
            <div className="text-[10px] font-mono text-muted uppercase">Model Divergence</div>
            <div className="text-2xl font-bold text-amber-400 font-mono mt-1">
              {history.length - unanimousCount}
            </div>
            <div className="text-[10px] text-muted mt-0.5">Requires biologist review</div>
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-surface-low p-3 rounded-xl border border-surface-highest">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
          <input
            type="text"
            placeholder="Search by predicted species, filename, or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 bg-surface-container rounded-lg border border-surface-highest text-xs text-on-surface focus:outline-none focus:border-primary placeholder:text-muted/60"
          />
        </div>

        <div className="flex items-center gap-1.5 text-xs">
          {(['all', 'unanimous', 'disagreement'] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => setFilterAgreement(mode)}
              className={`px-3 py-1.5 rounded-lg capitalize font-medium transition-all ${
                filterAgreement === mode
                  ? 'bg-primary text-background font-bold shadow-sm'
                  : 'bg-surface-container hover:bg-surface-high text-muted hover:text-white'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      {/* History Cards */}
      {filtered.length === 0 ? (
        <div className="h-64 rounded-2xl bg-surface-low border border-dashed border-surface-highest flex flex-col items-center justify-center text-muted text-center p-6">
          <History className="w-12 h-12 text-surface-highest mb-3" />
          <p className="text-base font-bold text-white mb-1">No Evaluation Records Found</p>
          <p className="text-xs text-muted max-w-sm">
            {history.length === 0
              ? 'Analyze fish specimens in the Recognition Workspace to build your audit log.'
              : 'No evaluations match your search and filter criteria.'}
          </p>
          {history.length === 0 && (
            <button
              onClick={() => navigate('/workspace')}
              className="mt-4 px-4 py-2 rounded-xl bg-primary text-background font-bold text-xs hover:bg-primary-light transition-all shadow glow-cyan"
            >
              Go to Workspace
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((item) => {
            const isUnanimous = item.agreementCount === item.totalModels;
            return (
              <div
                key={item.id}
                className="p-4 rounded-xl bg-surface-low border border-surface-highest hover:border-primary/40 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
              >
                <div className="flex items-center gap-4">
                  {/* Thumbnail */}
                  <div className="w-16 h-16 rounded-lg bg-black/60 overflow-hidden shrink-0 border border-surface-highest">
                    <img
                      src={item.imageSrc}
                      alt={item.predictedSpecies}
                      className="w-full h-full object-cover"
                    />
                  </div>

                  {/* Identification */}
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-bold text-white">{item.predictedSpecies}</h3>
                      <span className="text-[10px] font-mono text-muted">// {item.id}</span>
                    </div>
                    <div className="text-xs italic text-muted font-serif">{item.scientificName}</div>
                    <div className="flex items-center gap-2 text-[10px] text-muted mt-1 font-mono">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(item.timestamp).toLocaleString()}
                      </span>
                      <span>•</span>
                      <span>{item.filename}</span>
                    </div>
                  </div>
                </div>

                {/* Agreement & 5-Model Snapshot */}
                <div className="flex flex-col sm:items-end gap-1.5 w-full sm:w-auto">
                  <div
                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-bold ${
                      isUnanimous
                        ? 'bg-emerald-950/60 border border-emerald-500/60 text-emerald-300'
                        : 'bg-amber-950/60 border border-amber-500/60 text-amber-300'
                    }`}
                  >
                    {isUnanimous ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                    )}
                    <span>
                      {item.agreementCount} of {item.totalModels} Models Agreed
                    </span>
                  </div>

                  <div className="flex items-center gap-1">
                    {item.results.map((r) => (
                      <span
                        key={r.model}
                        title={`${r.model}: ${r.prediction} (${r.confidence.toFixed(1)}%)`}
                        className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-surface-container border border-surface-highest text-muted"
                      >
                        {r.model.split(' ')[0]}: {r.confidence.toFixed(0)}%
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
