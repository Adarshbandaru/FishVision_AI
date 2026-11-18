export interface TopPrediction {
  species: string;
  confidence: number;
}

export interface DisagreeingModel {
  model: string;
  predicted: string;
  confidence: number;
}

export interface ModelResult {
  model: string;
  prediction: string;
  confidence: number;
  top5: TopPrediction[];
  latency_ms?: number;
}

export interface Consensus {
  species: string;
  agreement_count: number;
  total_models: number;
  is_unanimous: boolean;
  has_disagreement: boolean;
  agreeing_models?: string[];
  disagreeing_models?: DisagreeingModel[];
  agreement_percentage?: number;
}

export interface PredictionResponse {
  results: ModelResult[];
  best_model: string;
  consensus: Consensus;
  total_latency_ms?: number;
  note: string;
}

export interface SpeciesMetadata {
  common_name: string;
  scientific_name: string;
  water_type: string;
  habitat: string;
  diet: string;
  typical_size: string;
  conservation_status: string;
  distribution?: string;
  key_identifiers?: string;
  depth_range?: string;
}

export interface SpeciesMap {
  [className: string]: SpeciesMetadata;
}

export interface BenchmarkMetric {
  model: string;
  accuracy: number;
  macro_precision: number;
  macro_recall: number;
  macro_f1: number;
  weighted_f1: number | null;
  latency_ms?: number;
  params_m?: number;
}

export interface DatasetSplit {
  classes: number;
  train: number;
  validation: number;
  test: number;
  total: number;
}

export interface BenchmarksResponse {
  dataset: DatasetSplit;
  metrics: BenchmarkMetric[];
  note: string;
}

export interface SampleSpecimen {
  id: string;
  class_name: string;
  filename: string;
  common_name: string;
  scientific_name: string;
  water_type: string;
  habitat: string;
  diet: string;
  typical_size: string;
  conservation_status: string;
  file_size_bytes: number;
}

export interface DetectionBox {
  box_2d: [number, number, number, number]; // [ymin, xmin, ymax, xmax] normalized
  pixel_box: [number, number, number, number];
  confidence: number;
  label: string;
  source: string;
}

export interface SegmentationResult {
  status: string;
  segmentation_type: string;
  primary_roi: DetectionBox;
  polygon_normalized: [number, number][];
  mask_coverage_pct: number;
}

export interface CVStatusResponse {
  yolo_detection: {
    available: boolean;
    weights_path: string | null;
    status: string;
  };
  sam_segmentation: {
    available: boolean;
    weights_path: string | null;
    status: string;
  };
  cpu_fallback: {
    available: boolean;
    mode: string;
    status: string;
  };
  device: string;
}

export interface HistoryItem {
  id: string;
  timestamp: string;
  filename: string;
  imageSrc: string;
  predictedSpecies: string;
  scientificName: string;
  agreementCount: number;
  totalModels: number;
  results: ModelResult[];
}

