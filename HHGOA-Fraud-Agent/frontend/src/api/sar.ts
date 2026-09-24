import { apiClient } from './client';
import type { ApiResponse } from '../types/api';
import type { SarRecord } from '../types/sar';

export async function fetchSarByCaseId(caseId: string): Promise<SarRecord | null> {
  const res = await apiClient.get<ApiResponse<SarRecord>>(`/api/investigations/${encodeURIComponent(caseId)}/sar`);
  return res.data.data;
}
