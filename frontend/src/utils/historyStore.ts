import type { HistoryItem, ModelResult } from '../types';

const STORAGE_KEY = 'fishvision_prediction_history_v2';

export const historyStore = {
  getHistory: (): HistoryItem[] => {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  },

  addEntry: (
    filename: string,
    imageSrc: string,
    predictedSpecies: string,
    scientificName: string,
    results: ModelResult[],
    agreementCount: number,
    totalModels: number
  ): HistoryItem => {
    const newItem: HistoryItem = {
      id: `SPEC-${Date.now().toString(36).toUpperCase()}`,
      timestamp: new Date().toISOString(),
      filename,
      imageSrc,
      predictedSpecies,
      scientificName,
      agreementCount,
      totalModels,
      results,
    };

    try {
      const history = historyStore.getHistory();
      const updated = [newItem, ...history].slice(0, 50); // keep last 50
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    } catch (e) {
      console.error('Failed to save prediction to history:', e);
    }

    return newItem;
  },

  clearHistory: () => {
    localStorage.removeItem(STORAGE_KEY);
  },
};
