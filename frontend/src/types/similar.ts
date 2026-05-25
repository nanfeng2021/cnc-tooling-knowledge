export interface SimilarCutter {
  cutter_id: string;
  cutter_name: string;
  similarity_score: number;
  category: string;
  diameter: number;
  substrate: string;
}

export interface SimilarToolResponse {
  source_cutter_id: string;
  source_cutter_name: string;
  similar_cutters: SimilarCutter[];
  count: number;
}
