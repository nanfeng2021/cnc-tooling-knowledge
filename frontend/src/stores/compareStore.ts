import { create } from "zustand";
import type { Cutter } from "@/types/cutter";

interface CompareState {
  items: Cutter[];
  addItem: (cutter: Cutter) => void;
  removeItem: (id: string) => void;
  clearAll: () => void;
  isInCompare: (id: string) => boolean;
}

export const useCompareStore = create<CompareState>((set, get) => ({
  items: [],
  addItem: (cutter) => {
    const { items } = get();
    if (items.length >= 4) return;
    if (items.some((c) => c.id === cutter.id)) return;
    set({ items: [...items, cutter] });
  },
  removeItem: (id) => {
    set({ items: get().items.filter((c) => c.id !== id) });
  },
  clearAll: () => set({ items: [] }),
  isInCompare: (id) => get().items.some((c) => c.id === id),
}));
