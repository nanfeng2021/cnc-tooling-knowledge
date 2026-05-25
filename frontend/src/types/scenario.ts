import type { Cutter } from "./cutter";

export interface MachiningScenario {
  category: string;
  material_iso_code: string;
  subcategory?: string;
  variant?: string;
  target_diameter?: number;
  manufacturer_id?: string;
  top_k?: number;
  min_score?: number;
}

export interface ScenarioMatchResult {
  cutter: Cutter;
  score: number;
  score_breakdown: Record<string, number>;
}

export interface ScenarioMatchResponse {
  items: ScenarioMatchResult[];
  total: number;
}
