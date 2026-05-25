import { create } from "zustand";
import type { MachiningScenario, ScenarioMatchResult } from "@/types/scenario";
import { scenarioService } from "@/api/client";

interface ScenarioState {
  results: ScenarioMatchResult[];
  total: number;
  loading: boolean;
  error: string | null;
  matchScenario(scenario: MachiningScenario): Promise<void>;
  reset(): void;
}

export const useScenarioStore = create<ScenarioState>((set) => ({
  results: [],
  total: 0,
  loading: false,
  error: null,
  matchScenario: async (scenario) => {
    set({ loading: true, error: null });
    try {
      const resp = await scenarioService.match(scenario);
      set({ results: resp.items, total: resp.total, loading: false });
    } catch (e) {
      set({ error: e instanceof Error ? e.message : "Unknown error", loading: false });
    }
  },
  reset: () => set({ results: [], total: 0, error: null }),
}));
