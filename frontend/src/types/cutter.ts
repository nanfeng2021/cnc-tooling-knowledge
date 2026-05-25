export interface CutterType {
  category: string;
  subcategory: string;
  variant?: string;
}

export interface MaterialSpec {
  substrate: string;
  coating_type?: string;
  hardness_hrc?: number;
  iso_class?: string;
}

export interface GeometryParams {
  diameter: number;
  length: number;
  flute_length: number;
  number_of_flutes: number;
  helix_angle: number;
  corner_radius: number;
}

export interface Cutter {
  id: string;
  name: string;
  cutter_type: CutterType;
  material: MaterialSpec;
  geometry: GeometryParams;
  recommended_parameters: Record<string, number>;
  usage_guidelines: string[];
  compatible_materials: string[];
  manufacturer_id?: string;
  model_number?: string;
  image_url?: string;
}

export interface SearchResult {
  cutter: Cutter;
  relevance_score: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}
