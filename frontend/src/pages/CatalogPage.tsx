import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  BookOpen,
  Search,
  Microscope,
  Info,
  X,
  Waves,
} from 'lucide-react';
import { api } from '../services/api';
import type { SpeciesMap, SpeciesMetadata, SampleSpecimen } from '../types';

export const CatalogPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [speciesMap, setSpeciesMap] = useState<SpeciesMap>({});
  const [samplesMap, setSamplesMap] = useState<Record<string, SampleSpecimen>>({});
  const [loading, setLoading] = useState(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [filterWater, setFilterWater] = useState<string>('all');
  const [selectedSpecies, setSelectedSpecies] = useState<{
    name: string;
    meta: SpeciesMetadata;
  } | null>(null);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) setSearchQuery(q);
  }, [searchParams]);

  useEffect(() => {
    Promise.all([api.getSpecies(), api.getSamplesManifest()])
      .then(([speciesData, samplesData]) => {
        setSpeciesMap(speciesData);
        const sMap: Record<string, SampleSpecimen> = {};
        samplesData.forEach((s) => {
          sMap[s.class_name.toLowerCase()] = s;
        });
        setSamplesMap(sMap);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const speciesList = Object.entries(speciesMap).map(([className, meta]) => ({
    className,
    meta,
    sample: samplesMap[className.toLowerCase()],
  }));

  const filtered = speciesList.filter(({ className, meta }) => {
    const query = searchQuery.toLowerCase();
    const matchesSearch =
      className.toLowerCase().includes(query) ||
      meta.common_name.toLowerCase().includes(query) ||
      meta.scientific_name.toLowerCase().includes(query) ||
      meta.habitat.toLowerCase().includes(query);

    const matchesWater =
      filterWater === 'all' ||
      meta.water_type.toLowerCase().includes(filterWater.toLowerCase());

    return matchesSearch && matchesWater;
  });

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-surface-low border border-surface-highest p-5 rounded-2xl">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <BookOpen className="w-6 h-6 text-primary" />
            152 Species Information Catalog
          </h1>
          <p className="text-xs text-muted mt-0.5">
            Peer-reviewed ecological taxonomy, habitat distribution, and morphological profiles.
          </p>
        </div>

        {/* Filter Bar */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[240px]">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
            <input
              type="text"
              placeholder="Search taxa, common name, or habitat..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-surface-container rounded-xl border border-surface-highest text-xs text-on-surface focus:outline-none focus:border-primary placeholder:text-muted/60"
            />
          </div>

          <div className="flex items-center gap-1.5 text-xs bg-surface-container p-1 rounded-xl border border-surface-highest">
            {['all', 'marine', 'freshwater', 'brackish'].map((type) => (
              <button
                key={type}
                onClick={() => setFilterWater(type)}
                className={`px-3 py-1.5 rounded-lg capitalize font-medium transition-all ${
                  filterWater === type
                    ? 'bg-primary text-background font-bold shadow-sm'
                    : 'text-muted hover:text-white'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Species Grid */}
      {loading ? (
        <div className="h-64 flex flex-col items-center justify-center text-muted">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mb-3" />
          <p className="text-sm font-mono">Indexing 152 species taxonomic database...</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="h-64 flex flex-col items-center justify-center text-muted">
          <Waves className="w-12 h-12 text-surface-highest mb-2" />
          <p className="text-base font-semibold">No matching species found</p>
          <p className="text-xs text-muted/60">Try adjusting your search query or water type filter.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filtered.map(({ className, meta, sample }) => (
            <div
              key={className}
              className="group bg-surface-low border border-surface-highest hover:border-primary/50 rounded-2xl overflow-hidden flex flex-col justify-between transition-all hover:-translate-y-1 hover:shadow-xl"
            >
              {/* Thumbnail */}
              <div
                onClick={() => setSelectedSpecies({ name: className, meta })}
                className="aspect-[4/3] bg-surface-lowest relative cursor-pointer overflow-hidden"
              >
                {sample ? (
                  <img
                    src={api.getSampleImageUrl(sample.filename)}
                    alt={meta.common_name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-muted">
                    <BookOpen className="w-8 h-8 opacity-40" />
                  </div>
                )}
                <div className="absolute top-2 left-2 bg-black/70 backdrop-blur-sm px-2 py-0.5 rounded text-[10px] font-mono text-secondary font-semibold">
                  {meta.water_type.split('/')[0].trim()}
                </div>
              </div>

              {/* Body */}
              <div className="p-4 flex flex-col justify-between flex-1 space-y-3">
                <div
                  onClick={() => setSelectedSpecies({ name: className, meta })}
                  className="cursor-pointer"
                >
                  <h3 className="text-sm font-bold text-white group-hover:text-primary transition-colors line-clamp-1">
                    {meta.common_name || className}
                  </h3>
                  <p className="text-xs italic text-muted font-serif line-clamp-1 mt-0.5">
                    {meta.scientific_name || className}
                  </p>
                </div>

                <div className="text-[11px] text-muted line-clamp-2 leading-relaxed">
                  {meta.habitat}
                </div>

                {/* Actions */}
                <div className="pt-3 border-t border-surface-highest/60 flex items-center justify-between text-xs">
                  <button
                    onClick={() => setSelectedSpecies({ name: className, meta })}
                    className="text-muted hover:text-white flex items-center gap-1 font-mono text-[11px]"
                  >
                    <Info className="w-3.5 h-3.5" /> Details
                  </button>

                  <button
                    onClick={() => {
                      if (sample) {
                        navigate('/workspace', { state: { selectedSample: sample } });
                      } else {
                        navigate('/workspace');
                      }
                    }}
                    className="px-2.5 py-1 rounded-lg bg-surface-container hover:bg-primary hover:text-background border border-surface-highest text-primary text-[11px] font-bold transition-all flex items-center gap-1"
                  >
                    <Microscope className="w-3 h-3" />
                    <span>Analyze</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      {selectedSpecies && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
          <div className="relative w-full max-w-2xl bg-surface-low border border-surface-highest rounded-2xl shadow-2xl p-6 overflow-hidden">
            <div className="flex items-start justify-between mb-4">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-secondary">
                  Taxon Profile // {selectedSpecies.name}
                </span>
                <h2 className="text-2xl font-bold text-white">
                  {selectedSpecies.meta.common_name}
                </h2>
                <p className="text-sm italic text-muted font-serif">
                  {selectedSpecies.meta.scientific_name}
                </p>
              </div>
              <button
                onClick={() => setSelectedSpecies(null)}
                className="p-1.5 rounded-lg bg-surface-highest/60 hover:bg-surface-highest text-muted hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs py-3 border-y border-surface-highest">
              <div>
                <span className="text-muted font-mono uppercase text-[10px]">Water Type</span>
                <div className="text-on-surface font-semibold mt-0.5">
                  {selectedSpecies.meta.water_type}
                </div>
              </div>

              <div>
                <span className="text-muted font-mono uppercase text-[10px]">Conservation Status</span>
                <div className="text-secondary font-semibold mt-0.5">
                  {selectedSpecies.meta.conservation_status}
                </div>
              </div>

              <div>
                <span className="text-muted font-mono uppercase text-[10px]">Typical Size</span>
                <div className="text-on-surface font-semibold mt-0.5">
                  {selectedSpecies.meta.typical_size}
                </div>
              </div>

              <div>
                <span className="text-muted font-mono uppercase text-[10px]">Class ID</span>
                <div className="text-on-surface font-mono font-semibold mt-0.5">
                  {selectedSpecies.name}
                </div>
              </div>
            </div>

            <div className="space-y-3 pt-3 text-xs">
              <div>
                <strong className="text-muted font-mono uppercase text-[10px] block mb-1">
                  Habitat & Geographic Distribution
                </strong>
                <p className="text-on-surface leading-relaxed">{selectedSpecies.meta.habitat}</p>
              </div>

              <div>
                <strong className="text-muted font-mono uppercase text-[10px] block mb-1">
                  Diet & Trophic Biology
                </strong>
                <p className="text-on-surface leading-relaxed">{selectedSpecies.meta.diet}</p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-surface-highest flex justify-end gap-3">
              <button
                onClick={() => setSelectedSpecies(null)}
                className="px-4 py-2 rounded-xl bg-surface-container text-xs text-muted hover:text-white"
              >
                Close
              </button>
              <button
                onClick={() => {
                  const s = samplesMap[selectedSpecies.name.toLowerCase()];
                  setSelectedSpecies(null);
                  if (s) {
                    navigate('/workspace', { state: { selectedSample: s } });
                  } else {
                    navigate('/workspace');
                  }
                }}
                className="px-4 py-2 rounded-xl bg-primary text-background font-bold text-xs hover:bg-primary-light flex items-center gap-1.5 shadow-md glow-cyan"
              >
                <Microscope className="w-3.5 h-3.5" />
                <span>Test in Workspace</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
