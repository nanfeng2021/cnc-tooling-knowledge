import { create } from "zustand";
import type { QAResponse } from "@/types/qa";
import { qaService } from "@/api/client";

interface QAState {
  result: QAResponse | null;
  loading: boolean;
  error: string | null;
  askQuestion: (question: string, topK?: number) => Promise<void>;
  reset: () => void;
}

export const useQAStore = create<QAState>((set) => ({
  result: null,
  loading: false,
  error: null,
  askQuestion: async (question, topK) => {
    set({ loading: true, error: null });
    try {
      const result = await qaService.ask(question, topK);
      set({ result, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },
  reset: () => set({ result: null, error: null }),
}));
