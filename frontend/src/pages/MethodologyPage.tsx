import React from 'react';
import {
  Layers,
  Cpu,
  AlertTriangle,
  Database,
} from 'lucide-react';

export const MethodologyPage: React.FC = () => {
  return (
    <div className="p-6 lg:p-8 max-w-5xl mx-auto space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="bg-surface-low border border-surface-highest p-6 rounded-2xl space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono uppercase tracking-wider text-primary bg-surface-container px-2.5 py-0.5 rounded-full border border-primary/20">
            Academic Technical Documentation
          </span>
          <span className="text-xs font-mono text-muted">// REF: FV2-RES-2026</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          Methodology & Neural Ensemble Architecture
        </h1>
        <p className="text-sm text-muted leading-relaxed">
          Technical specifications, evaluation protocols, and architectural trade-offs for the
          152-class marine specimen recognition benchmark.
        </p>
      </div>

      {/* 1. Dataset Split & Integrity */}
      <section className="bg-surface-low border border-surface-highest p-6 rounded-2xl space-y-4">
        <div className="flex items-center gap-2.5 text-primary">
          <Database className="w-5 h-5" />
          <h2 className="text-lg font-bold text-white">Dataset Partitioning & Taxonomic Integrity</h2>
        </div>
        <p className="text-xs text-muted leading-relaxed">
          The FishVision dataset comprises <strong>22,741 high-resolution images</strong> across{' '}
          <strong>152 distinct marine, brackish, and freshwater fish taxa</strong>. The evaluation
          protocol strictly segregates samples into non-overlapping partitions to prevent data
          leakage:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
          <div className="p-4 rounded-xl bg-surface-container/60 border border-surface-highest">
            <div className="text-[10px] font-mono text-muted uppercase">Training Split</div>
            <div className="text-xl font-bold font-mono text-white mt-1">15,305 images</div>
            <div className="text-[11px] text-muted mt-0.5">67.3% total representation</div>
          </div>

          <div className="p-4 rounded-xl bg-surface-container/60 border border-surface-highest">
            <div className="text-[10px] font-mono text-muted uppercase">Validation Split</div>
            <div className="text-xl font-bold font-mono text-white mt-1">4,127 images</div>
            <div className="text-[11px] text-muted mt-0.5">18.1% hyperparameter tuning</div>
          </div>

          <div className="p-4 rounded-xl bg-surface-container/60 border border-secondary/40">
            <div className="text-[10px] font-mono text-secondary uppercase">Held-Out Test Split</div>
            <div className="text-xl font-bold font-mono text-secondary mt-1">3,309 images</div>
            <div className="text-[11px] text-secondary mt-0.5">14.5% frozen benchmark</div>
          </div>
        </div>
      </section>

      {/* 2. Architectural Comparison (5 Backbones) */}
      <section className="bg-surface-low border border-surface-highest p-6 rounded-2xl space-y-4">
        <div className="flex items-center gap-2.5 text-primary">
          <Cpu className="w-5 h-5" />
          <h2 className="text-lg font-bold text-white">Five Distinct Neural Architectural Paradigms</h2>
        </div>
        <p className="text-xs text-muted leading-relaxed">
          Rather than relying on a single architecture, FishVision benchmarks five diverse deep
          learning backbones spanning self-supervised transformers, hierarchical vision
          transformers, modern pure CNNs, and edge-optimized mobile models:
        </p>

        <div className="space-y-3 pt-2">
          {/* DINOv2 */}
          <div className="p-4 rounded-xl bg-surface-container/40 border border-primary/40 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-white text-sm">DINOv2 (ViT-B/14 with Registers)</span>
                <span className="text-[10px] font-mono bg-primary text-background font-bold px-1.5 py-0.5 rounded">
                  93.90% SOTA Peak
                </span>
              </div>
              <span className="text-xs font-mono text-muted">518x518 Res • 86M Params</span>
            </div>
            <p className="text-xs text-muted leading-relaxed">
              Self-supervised Vision Transformer with register tokens to eliminate artifactual high-norm
              tokens. Its multi-head self-attention enables fine-grained morphological feature
              extraction (fin rays, scale patterns, operculum edges) invariant to water turbidity and
              caustic illumination.
            </p>
          </div>

          {/* ViT-B/16 */}
          <div className="p-4 rounded-xl bg-surface-container/40 border border-surface-highest space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-white text-sm">ViT-B/16 (Supervised Patch-16)</span>
                <span className="text-[10px] font-mono bg-secondary/20 text-secondary border border-secondary/30 px-1.5 py-0.5 rounded">
                  88.33% Accuracy
                </span>
              </div>
              <span className="text-xs font-mono text-muted">224x224 Res • 86M Params</span>
            </div>
            <p className="text-xs text-muted leading-relaxed">
              Standard pure transformer architecture operating on non-overlapping 16x16 image patches.
              Provides strong global spatial reasoning but requires careful regularization on smaller
              classes.
            </p>
          </div>

          {/* ConvNeXt Tiny */}
          <div className="p-4 rounded-xl bg-surface-container/40 border border-surface-highest space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-white text-sm">ConvNeXt Tiny</span>
                <span className="text-[10px] font-mono bg-secondary/20 text-secondary border border-secondary/30 px-1.5 py-0.5 rounded">
                  87.40% Accuracy
                </span>
              </div>
              <span className="text-xs font-mono text-muted">224x224 Res • 28M Params</span>
            </div>
            <p className="text-xs text-muted leading-relaxed">
              A modernized pure convolutional architecture adopting ViT design practices (7x7
              depthwise separable convolutions, inverted bottleneck, GELU activations). Extremely
              efficient and robust to local edge textures.
            </p>
          </div>

          {/* Swin Tiny */}
          <div className="p-4 rounded-xl bg-surface-container/40 border border-surface-highest space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-white text-sm">Swin Tiny (Shifted Window ViT)</span>
                <span className="text-[10px] font-mono bg-secondary/20 text-secondary border border-secondary/30 px-1.5 py-0.5 rounded">
                  85.13% Accuracy
                </span>
              </div>
              <span className="text-xs font-mono text-muted">224x224 Res • 28M Params</span>
            </div>
            <p className="text-xs text-muted leading-relaxed">
              Hierarchical Vision Transformer that computes self-attention within non-overlapping local
              windows while allowing cross-window connections via shifted window partitioning.
            </p>
          </div>

          {/* MobileNetV3 */}
          <div className="p-4 rounded-xl bg-surface-container/40 border border-surface-highest space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-white text-sm">MobileNetV3 Large</span>
                <span className="text-[10px] font-mono bg-surface-highest text-muted px-1.5 py-0.5 rounded">
                  70.32% Accuracy
                </span>
              </div>
              <span className="text-xs font-mono text-muted">224x224 Res • 5.4M Params</span>
            </div>
            <p className="text-xs text-muted leading-relaxed">
              Hardware-aware neural architecture search design for resource-constrained edge marine
              drones. Trades top-1 accuracy for sub-20ms inference latency on low-power ARM devices.
            </p>
          </div>
        </div>
      </section>

      {/* 3. Softmax Confidence Calibration Caveat */}
      <section className="bg-amber-950/20 border border-amber-500/50 p-6 rounded-2xl space-y-3">
        <div className="flex items-center gap-2 text-amber-300">
          <AlertTriangle className="w-5 h-5 shrink-0" />
          <h2 className="text-base font-bold">
            Methodological Notice: Softmax Confidence is Not Calibrated Probability
          </h2>
        </div>
        <p className="text-xs text-amber-200/90 leading-relaxed">
          In high-capacity deep neural networks, uncalibrated softmax output probabilities frequently
          exhibit overconfidence on out-of-distribution or degraded underwater imagery. A 98% softmax
          confidence from MobileNetV3 cannot be compared as equivalent to a 98% confidence from
          DINOv2.
        </p>
        <p className="text-xs text-amber-200/90 leading-relaxed">
          FishVision addresses this by presenting the <strong>Ensemble Consensus</strong> across all
          5 diverse model families. When models disagree on a specimen, the platform explicitly
          surfaces a divergence warning rather than relying solely on the single highest softmax
          probability.
        </p>
      </section>

      {/* 4. Inference Pipeline & TTA */}
      <section className="bg-surface-low border border-surface-highest p-6 rounded-2xl space-y-3">
        <div className="flex items-center gap-2.5 text-primary">
          <Layers className="w-5 h-5" />
          <h2 className="text-lg font-bold text-white">
            Test-Time Augmentation (TTA) & Multi-Crop Strategy
          </h2>
        </div>
        <p className="text-xs text-muted leading-relaxed">
          To accommodate variable fish aspect ratios without discarding critical tail and dorsal fin
          cues, FishVision executes a multi-view ensembling strategy at inference time:
        </p>
        <ul className="space-y-2 text-xs text-on-surface list-disc list-inside">
          <li>
            <strong>Full-Square Resize:</strong> Captures the complete fish silhouette, preserving
            holistic body shape and fin positioning.
          </li>
          <li>
            <strong>Aspect-Preserving Center Crop:</strong> Resizes the shorter axis and crops the
            center, preserving high-frequency textural resolution of scales and head morphology.
          </li>
          <li>
            <strong>Logit Averaging:</strong> The probabilities from both views are averaged prior to
            top-k extraction.
          </li>
        </ul>
      </section>
    </div>
  );
};
