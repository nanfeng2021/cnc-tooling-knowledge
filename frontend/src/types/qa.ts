export interface QASource {
  cutter_id: string;
  cutter_name: string;
  relevance_score: number;
  category: string;
  diameter: number;
  summary: string;
}

export interface QAResponse {
  question: string;
  answer: string;
  sources: QASource[];
  confidence: number;
}
