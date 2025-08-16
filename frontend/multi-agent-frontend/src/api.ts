import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export interface ResearchRequest {
  topic: string;
  num_results: number;
  report_style: string;
}

export interface SearchResult {
  url: string;
  title: string;
  snippet: string;
  content_preview?: string;
  fetched_text_length?: number;
}

export interface ResearchResponse {
  research_results: SearchResult[];
  analysis_summary: string;
  analysis_tables: Record<string, any>;
  draft_report: string;
  final_report: string;
  review_notes: string;
  processing_time?: number;
  agent_logs?: Record<string, any>;
}

export const researchApi = {
  generateReport: async (request: ResearchRequest): Promise<ResearchResponse> => {
    const response = await axios.post<ResearchResponse>(`${API_BASE_URL}/research`, request);
    return response.data;
  }
};