import React, { useState, useEffect } from 'react';
import { X, Search, Sparkles, Filter, CheckCircle2, Waves } from 'lucide-react';
import type { SampleSpecimen } from '../types';
import { api } from '../services/api';

interface SampleGalleryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSample: (sample: SampleSpecimen) => void;
}

export const SampleGalleryModal: React.FC<SampleGalleryModalProps> = ({
  isOpen,
  onClose,
  onSelectSample,
}) => {
  const [samples, setSamples] = useState<SampleSpecimen[]>([]);
  const [search, setSearch] = useState('');
  const [filterWater, setFilterWater] = useState<string>('all');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && samples.length === 0) {
      setLoading(true);
      api
        .getSamplesManifest()
        .then((data) => setSamples(data))
        .catch((err) => console.error('Failed to load gallery samples:', err))
        .finally(() => setLoading(false));
    }
  }, [isOpen, samples.length]);

  if (!isOpen) return null;

  const filtered = samples.filter((s) => {
    const matchesSearch =
      s.common_name.toLowerCase().includes(search.toLowerCase()) ||
      s.class_name.toLowerCase().includes(search.toLowerCase()) ||
      s.scientific_name.toLowerCase().includes(search.toLowerCase()) ||
      s.habitat.toLowerCase().includes(search.toLowerCase());

    const matchesWater =
      filterWater === 'all' ||
      s.water_type.toLowerCase().includes(filterWater.toLowerCase());

    return matchesSearch && matchesWater;
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-5xl h-[85vh] bg-surface-low border border-surface-highest rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-surface-highest flex items-center justify-between bg-surface-container/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/30 flex items-center justify-center text-primary">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-primary flex items-center gap-2">
                Authentic Specimen Gallery
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-surface-highest text-secondary">
                  152 Taxa Verified
                </span>
              </h2>
              <p className="text-xs text-muted">
                Curated held-out test specimens sourced directly from the 152-class marine biology dataset.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-surface-highest/60 hover:bg-surface-highest text-muted hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filter Controls */}
        <div className="p-4 border-b border-surface-high flex flex-wrap items-center justify-between gap-3 bg-surface-lowest/40">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
            <input
              type="text"
              placeholder="Filter by common name, scientific name, or habitat..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-surface-container rounded-lg border border-surface-highest text-sm text-on-surface focus:outline-none focus:border-primary placeholder:text-muted/60"
            />
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-muted flex items-center gap-1 font-mono">
              <Filter className="w-3.5 h-3.5" /> WATER:
            </span>
            {['all', 'marine', 'freshwater', 'brackish'].map((type) => (
              <button
                key={type}
                onClick={() => setFilterWater(type)}
                className={`px-3 py-1.5 rounded-lg capitalize font-medium transition-all ${
                  filterWater === type
                    ? 'bg-primary text-background font-bold shadow-sm'
                    : 'bg-surface-container hover:bg-surface-high text-muted hover:text-white'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Specimen Grid */}
        <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
          {loading ? (
            <div className="h-full flex flex-col items-center justify-center gap-3 text-muted">
              <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              <p className="text-sm font-mono">Loading authentic specimens manifest...</p>
            </div>
          ) : filtered.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-muted">
              <Waves className="w-12 h-12 text-muted/40 mb-2" />
              <p className="text-base font-semibold">No matching specimens found</p>
              <p className="text-xs text-muted/60">Try clearing your search query or water filter.</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
              {filtered.map((item) => (
                <div
                  key={item.id}
                  onClick={() => {
                    onSelectSample(item);
                    onClose();
                  }}
                  className="group relative bg-surface-container/70 border border-surface-high hover:border-primary/50 rounded-xl overflow-hidden cursor-pointer transition-all hover:-translate-y-1 hover:shadow-lg flex flex-col"
                >
                  <div className="aspect-[4/3] w-full bg-surface-lowest relative overflow-hidden">
                    <img
                      src={api.getSampleImageUrl(item.filename)}
                      alt={item.common_name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      loading="lazy"
                    />
                    <div className="absolute top-1.5 left-1.5 bg-black/60 backdrop-blur-sm px-1.5 py-0.5 rounded text-[10px] font-mono text-secondary font-medium">
                      {item.id}
                    </div>
                  </div>
                  <div className="p-2.5 flex flex-col justify-between flex-1">
                    <div>
                      <h4 className="text-xs font-bold text-on-surface group-hover:text-primary transition-colors line-clamp-1">
                        {item.common_name}
                      </h4>
                      <p className="text-[11px] italic text-muted line-clamp-1">
                        {item.scientific_name}
                      </p>
                    </div>
                    <div className="mt-2 pt-2 border-t border-surface-highest/50 flex items-center justify-between text-[10px]">
                      <span className="text-muted/80 truncate max-w-[80px]">
                        {item.water_type.split('/')[0].trim()}
                      </span>
                      <span className="text-primary font-mono font-medium flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                        Select <CheckCircle2 className="w-3 h-3" />
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-surface-high bg-surface-container/30 px-5 flex items-center justify-between text-xs text-muted">
          <span>
            Showing <strong className="text-primary">{filtered.length}</strong> of{' '}
            {samples.length} cataloged taxa
          </span>
          <span className="font-mono text-[11px]">Click any specimen to load into Workspace</span>
        </div>
      </div>
    </div>
  );
};
