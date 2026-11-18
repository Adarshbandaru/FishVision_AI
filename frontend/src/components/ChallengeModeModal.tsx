import React, { useState, useEffect } from 'react';
import {
  X,
  Trophy,
  Brain,
  HelpCircle,
  ArrowRight,
  CheckCircle2,
  XCircle,
  RotateCw,
  Flame,
  Award,
} from 'lucide-react';
import type { SampleSpecimen, ModelResult, Consensus } from '../types';
import { api } from '../services/api';

interface ChallengeModeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ChallengeModeModal: React.FC<ChallengeModeModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [samples, setSamples] = useState<SampleSpecimen[]>([]);
  const [currentSample, setCurrentSample] = useState<SampleSpecimen | null>(null);
  const [options, setOptions] = useState<string[]>([]);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isRevealed, setIsRevealed] = useState(false);
  const [showHint, setShowHint] = useState(false);

  // Score state
  const [score, setScore] = useState(0);
  const [totalAttempts, setTotalAttempts] = useState(0);
  const [streak, setStreak] = useState(0);

  // AI comparison on reveal
  const [aiLoading, setAiLoading] = useState(false);
  const [aiConsensus, setAiConsensus] = useState<Consensus | null>(null);
  const [aiResults, setAiResults] = useState<ModelResult[]>([]);

  useEffect(() => {
    if (isOpen && samples.length === 0) {
      api.getSamplesManifest().then((data) => {
        setSamples(data);
        pickNextChallenge(data);
      });
    } else if (isOpen && samples.length > 0 && !currentSample) {
      pickNextChallenge(samples);
    }
  }, [isOpen, samples]);

  const pickNextChallenge = (manifest: SampleSpecimen[]) => {
    if (!manifest || manifest.length < 4) return;
    const randomIdx = Math.floor(Math.random() * manifest.length);
    const target = manifest[randomIdx];
    setCurrentSample(target);

    // Pick 3 random decoys
    const decoys: string[] = [];
    while (decoys.length < 3) {
      const dIdx = Math.floor(Math.random() * manifest.length);
      const d = manifest[dIdx].common_name;
      if (d !== target.common_name && !decoys.includes(d)) {
        decoys.push(d);
      }
    }

    // Shuffle options
    const all = [target.common_name, ...decoys].sort(() => Math.random() - 0.5);
    setOptions(all);
    setSelectedAnswer(null);
    setIsRevealed(false);
    setShowHint(false);
    setAiConsensus(null);
    setAiResults([]);
  };

  const handleSelectOption = async (option: string) => {
    if (isRevealed || !currentSample) return;
    setSelectedAnswer(option);
    setIsRevealed(true);
    setTotalAttempts((prev) => prev + 1);

    const isCorrect = option.toLowerCase() === currentSample.common_name.toLowerCase();
    if (isCorrect) {
      setScore((prev) => prev + 1);
      setStreak((prev) => prev + 1);
    } else {
      setStreak(0);
    }

    // Trigger 5-model AI inference on this exact specimen
    setAiLoading(true);
    try {
      const file = await api.fetchSampleImageFile(currentSample.filename);
      const pred = await api.predictImage(file);
      setAiConsensus(pred.consensus);
      setAiResults(pred.results);
    } catch (err) {
      console.warn('AI comparison inference skipped:', err);
    } finally {
      setAiLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-surface-low border border-surface-highest rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        {/* Header with Game Stats */}
        <div className="p-4 border-b border-surface-highest flex items-center justify-between bg-surface-container/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-secondary/10 border border-secondary/30 flex items-center justify-center text-secondary">
              <Trophy className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                Fish Recognition Challenge
                <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-secondary/20 text-secondary border border-secondary/30">
                  Human vs 5-Model AI
                </span>
              </h2>
              <p className="text-xs text-muted">
                Can you identify this authentic marine specimen faster than our ensemble neural networks?
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 bg-surface-highest/50 px-3 py-1.5 rounded-xl border border-surface-high">
              <div className="text-right">
                <div className="text-[10px] uppercase font-mono text-muted">Score</div>
                <div className="text-sm font-bold text-primary font-mono">
                  {score} / {totalAttempts}
                </div>
              </div>
              <div className="w-px h-6 bg-surface-high" />
              <div className="flex items-center gap-1 text-orange-400">
                <Flame className="w-4 h-4" />
                <span className="text-sm font-bold font-mono">{streak}</span>
              </div>
            </div>

            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-surface-highest/60 hover:bg-surface-highest text-muted hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-5 custom-scrollbar">
          {currentSample ? (
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
              {/* Image Preview Canvas */}
              <div className="md:col-span-6 flex flex-col gap-3">
                <div className="relative aspect-[4/3] rounded-xl overflow-hidden border border-surface-highest bg-black/60 shadow-inner group">
                  <img
                    src={api.getSampleImageUrl(currentSample.filename)}
                    alt="Mystery Fish"
                    className="w-full h-full object-contain"
                  />
                  <div className="absolute top-2 left-2 bg-black/70 backdrop-blur-sm px-2.5 py-1 rounded text-xs font-mono text-secondary">
                    Specimen: {currentSample.id}
                  </div>
                  {!isRevealed && (
                    <div className="absolute bottom-2 right-2 bg-black/70 backdrop-blur-sm px-2.5 py-1 rounded text-[11px] font-mono text-muted flex items-center gap-1">
                      <HelpCircle className="w-3.5 h-3.5 text-primary" /> Identify Taxa
                    </div>
                  )}
                </div>

                {/* Ecological Hint Toggle */}
                {!isRevealed ? (
                  <div className="bg-surface-container/50 border border-surface-high rounded-xl p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-muted flex items-center gap-1.5">
                        <Brain className="w-3.5 h-3.5 text-secondary" /> Need a field biologist clue?
                      </span>
                      <button
                        onClick={() => setShowHint(!showHint)}
                        className="text-xs font-mono text-primary hover:underline"
                      >
                        {showHint ? 'Hide Clue' : 'Reveal Clue'}
                      </button>
                    </div>
                    {showHint && (
                      <div className="mt-2 pt-2 border-t border-surface-highest/60 text-xs text-on-surface space-y-1 animate-fadeIn">
                        <div>
                          <strong className="text-muted font-mono">Habitat:</strong>{' '}
                          {currentSample.habitat}
                        </div>
                        <div>
                          <strong className="text-muted font-mono">Water Type:</strong>{' '}
                          {currentSample.water_type}
                        </div>
                        <div>
                          <strong className="text-muted font-mono">Diet:</strong>{' '}
                          {currentSample.diet}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="bg-surface-container/80 border border-secondary/30 rounded-xl p-3.5 space-y-2 animate-fadeIn">
                    <div className="flex items-center gap-2 text-secondary font-bold text-sm">
                      <Award className="w-4 h-4" /> Ground Truth Taxonomy
                    </div>
                    <div>
                      <div className="text-base font-bold text-primary">
                        {currentSample.common_name}
                      </div>
                      <div className="text-xs italic text-muted font-serif">
                        {currentSample.scientific_name}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 pt-2 text-[11px] text-muted border-t border-surface-highest">
                      <div>
                        <span className="font-mono text-muted/60">STATUS:</span>{' '}
                        <span className="text-on-surface">{currentSample.conservation_status}</span>
                      </div>
                      <div>
                        <span className="font-mono text-muted/60">SIZE:</span>{' '}
                        <span className="text-on-surface">{currentSample.typical_size}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Options Column */}
              <div className="md:col-span-6 flex flex-col gap-4">
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-muted font-mono mb-2">
                    Select the Correct Fish Species:
                  </h3>
                  <div className="space-y-2.5">
                    {options.map((opt) => {
                      const isTarget =
                        opt.toLowerCase() === currentSample.common_name.toLowerCase();
                      const isChosen = selectedAnswer === opt;

                      let btnStyle =
                        'bg-surface-container hover:bg-surface-high border-surface-high text-on-surface';

                      if (isRevealed) {
                        if (isTarget) {
                          btnStyle =
                            'bg-emerald-950/60 border-emerald-500/80 text-emerald-300 font-bold';
                        } else if (isChosen && !isTarget) {
                          btnStyle = 'bg-rose-950/60 border-rose-500/80 text-rose-300';
                        } else {
                          btnStyle = 'bg-surface-container/40 border-surface-high/30 text-muted/50';
                        }
                      }

                      return (
                        <button
                          key={opt}
                          disabled={isRevealed}
                          onClick={() => handleSelectOption(opt)}
                          className={`w-full p-3 rounded-xl border text-left text-sm transition-all flex items-center justify-between ${btnStyle}`}
                        >
                          <span>{opt}</span>
                          {isRevealed && isTarget && (
                            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                          )}
                          {isRevealed && isChosen && !isTarget && (
                            <XCircle className="w-5 h-5 text-rose-400 shrink-0" />
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* AI Model Verdict Comparison */}
                {isRevealed && (
                  <div className="p-3.5 bg-surface-lowest/70 border border-surface-highest rounded-xl space-y-2.5 animate-fadeIn">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono uppercase tracking-wider text-primary flex items-center gap-1.5">
                        <Brain className="w-3.5 h-3.5" /> 5-Model Ensemble Consensus
                      </span>
                      {aiLoading ? (
                        <span className="text-[10px] font-mono text-muted flex items-center gap-1">
                          <RotateCw className="w-3 h-3 animate-spin" /> Evaluating...
                        </span>
                      ) : aiConsensus ? (
                        <span className="text-xs font-mono font-bold text-secondary">
                          {aiConsensus.agreement_count} / {aiConsensus.total_models} Models Agreed
                        </span>
                      ) : null}
                    </div>

                    {aiResults.length > 0 && (
                      <div className="grid grid-cols-5 gap-1.5 pt-1">
                        {aiResults.map((m) => {
                          const matchesTarget =
                            m.prediction.toLowerCase() === currentSample.class_name.toLowerCase();
                          return (
                            <div
                              key={m.model}
                              className={`p-1.5 rounded-lg border text-center ${
                                matchesTarget
                                  ? 'bg-emerald-950/40 border-emerald-600/40'
                                  : 'bg-surface-container border-surface-highest'
                              }`}
                            >
                              <div className="text-[9px] font-mono text-muted truncate">
                                {m.model}
                              </div>
                              <div
                                className={`text-[11px] font-bold ${
                                  matchesTarget ? 'text-emerald-400' : 'text-rose-400'
                                }`}
                              >
                                {matchesTarget ? '✓' : '✗'}
                              </div>
                              <div className="text-[8px] font-mono text-muted/80">
                                {m.confidence.toFixed(0)}%
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}

                    <div className="pt-2">
                      <button
                        onClick={() => pickNextChallenge(samples)}
                        className="w-full py-2.5 px-4 bg-primary text-background font-bold rounded-xl text-sm hover:bg-primary-light transition-all flex items-center justify-center gap-2 shadow-lg glow-cyan"
                      >
                        Next Mystery Specimen <ArrowRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-muted">
              <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mb-3" />
              <p className="text-sm font-mono">Preparing randomized challenge specimen...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
