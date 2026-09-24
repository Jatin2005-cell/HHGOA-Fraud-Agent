import { apiClient } from './client';
import type { ApiResponse, SearchResult } from '../types/api';

export async function performGlobalSearch(query: string): Promise<SearchResult> {
  const res = await apiClient.get<ApiResponse<SearchResult>>('/api/search', {
    params: { q: query },
  });
  return res.data.data;
}
