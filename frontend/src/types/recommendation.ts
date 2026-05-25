import type { Cutter } from "./cutter";

export interface ParameterRange {
  min_value: number;
  max_value: number;
  avg_value: number;
  unit: string;
}

export interface ParameterRecommendation {
  workpiece_material: string;
  iso_code: string;
  operation_type: string;
  target_diameter: number | null;
  parameters: Record<string, ParameterRange>;
  source_cutters: Cutter[];
  candidate_count: number;
}
