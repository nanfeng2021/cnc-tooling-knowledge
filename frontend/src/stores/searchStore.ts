import { create } from "zustand";
import type { Cutter } from "@/types/cutter";
import { searchService } from "@/api/client";

interface SearchState {
  query: string;
  results: { cutter: Cutter; relevance_score: number }[];
  total: number;
  loading: boolean;
  setQuery: (q: string) => void;
  search: (q: string) => Promise<void>;
}

export const useSearchStore = create<SearchState>((set) => ({
  query: "",
  results: [],
  total: 0,
  loading: false,
  setQuery: (q) => set({ query: q }),
  search: async (q) => {
    if (!q.trim()) {
      set({ results: [], total: 0, query: q });
      return;
    }
    set({ loading: true, query: q });
    try {
      const res = await searchService.search(q, 50, 0);
      set({ results: res.items, total: res.total, loading: false });
    } catch {
      set({ loading: false });
    }
  },
}));
