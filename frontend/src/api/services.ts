import { apiClient } from './client';

export interface SourceDoc {
  content: string;
  metadata: Record<string, any>;
}

export interface QueryResponse {
  answer: string;
  sources: SourceDoc[];
  guardrail_triggered: boolean;
}

export const apiService = {
  // Auth
  login: async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await apiClient.post('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  // Query
  query: async (question: string, top_k = 5, use_hyde = false, multi_query = false): Promise<QueryResponse> => {
    const response = await apiClient.post('/query', {
      question,
      top_k,
      use_hyde,
      multi_query,
    });
    return response.data;
  },

  // Upload
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};
