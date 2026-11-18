import axios from 'axios';
import type {
  PredictionResponse,
  SpeciesMap,
  SpeciesMetadata,
  BenchmarksResponse,
  SampleSpecimen,
  CVStatusResponse,
  DetectionBox,
  SegmentationResult,
} from '../types';

const API_BASE = '/api';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 45000,
});

export const api = {
  // System Health & Telemetry
  checkHealth: async () => {
    const res = await client.get('/health');
    return res.data;
  },

  getModels: async () => {
    const res = await client.get('/models');
    return res.data.models;
  },

  getClasses: async (): Promise<string[]> => {
    const res = await client.get('/classes');
    return res.data.classes;
  },

  // Species Metadata
  getSpecies: async (): Promise<SpeciesMap> => {
    const res = await client.get('/species');
    return res.data.species;
  },

  getSpeciesByName: async (name: string): Promise<SpeciesMetadata> => {
    const res = await client.get(`/species/${encodeURIComponent(name)}`);
    return res.data;
  },

  // Benchmarks
  getBenchmarks: async (): Promise<BenchmarksResponse> => {
    const res = await client.get('/benchmarks');
    return res.data;
  },

  // Authentic Sample Manifest
  getSamplesManifest: async (): Promise<SampleSpecimen[]> => {
    const res = await client.get('/samples/manifest');
    return res.data.samples;
  },

  getRandomSample: async (species?: string): Promise<SampleSpecimen> => {
    const params = species ? { species } : {};
    const res = await client.get('/samples/random', { params });
    return res.data;
  },

  getSampleImageUrl: (filename: string): string => {
    return `/samples/image/${encodeURIComponent(filename)}`;
  },

  fetchSampleImageFile: async (filename: string): Promise<File> => {
    const res = await axios.get(`/samples/image/${encodeURIComponent(filename)}`, {
      responseType: 'blob',
    });
    const contentType = (res.headers['content-type'] as string) || 'image/jpeg';
    return new File([res.data], filename, { type: contentType });
  },

  // Prediction Inference
  predictImage: async (file: File): Promise<PredictionResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await client.post<PredictionResponse>('/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  // Computer Vision Modules
  getCVStatus: async (): Promise<CVStatusResponse> => {
    const res = await client.get('/cv/status');
    return res.data;
  },

  detectFishROI: async (file: File): Promise<{ detections: DetectionBox[]; count: number }> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await client.post('/cv/detect', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  segmentFishMask: async (file: File): Promise<SegmentationResult> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await client.post('/cv/segment', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  analyzeCombined: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await client.post('/cv/analyze-combined', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
};
