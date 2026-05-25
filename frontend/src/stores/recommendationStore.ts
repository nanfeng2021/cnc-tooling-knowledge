import { create } from "zustand";
import type { ParameterRecommendation } from "@/types/recommendation";
import { recommendationService } from "@/api/client";

interface RecommendationState {
  result: ParameterRecommendation | null;
  loading: boolean;
  error: string | null;
  fetchParameters(material: string, operation: string, diameter?: number): Promise<void>;
  reset(): void;
}

export const useRecommendationStore = create<RecommendationState>((set) => ({
  result: null,
  loading: false,
  error: null,
  fetchParameters: async (material, operation, diameter) => {
    set({ loading: true, error: null });
    try {
      const result = await recommendationService.getParameters(material, operation, diameter);
      set({ result, loading: false });
    } catch (e) {
      set({ error: e instanceof Error ? e.message : "Unknown error", loading: false });
    }
  },
  reset: () => set({ result: null, error: null }),
}));
