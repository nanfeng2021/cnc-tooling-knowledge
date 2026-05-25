import { create } from "zustand";
import type { GCodeSuggestion } from "@/types/gcode";
import { gcodeService } from "@/api/client";

interface GCodeState {
  result: GCodeSuggestion | null;
  loading: boolean;
  error: string | null;
  generate: (params: {
    cutterId: string;
    operation: string;
    workpieceMaterial: string;
    diameter?: number;
    width?: number;
    length?: number;
    depth?: number;
  }) => Promise<void>;
  reset: () => void;
}

export const useGCodeStore = create<GCodeState>((set) => ({
  result: null,
  loading: false,
  error: null,
  generate: async (params) => {
    set({ loading: true, error: null });
    try {
      const result = await gcodeService.generate(params);
      set({ result, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },
  reset: () => set({ result: null, error: null }),
}));
