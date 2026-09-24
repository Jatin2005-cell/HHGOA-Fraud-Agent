import { apiClient } from './client';
import type { ApiResponse } from '../types/api';

export interface AuditLogItem {
  timestamp: string;
  request_id: string;
  case_id: string;
  actor: string;
  operation: string;
  status: string;
  details: Record<string, any>;
}

export interface AuditLogResponse {
  items: AuditLogItem[];
  total: number;
  page: number;
  page_size: number;
}

export async function fetchAuditLogs(params: {
  case_id?: string;
  operation?: string;
  page?: number;
  page_size?: number;
} = {}): Promise<AuditLogResponse> {
  const res = await apiClient.get<ApiResponse<AuditLogResponse>>('/api/audit', { params });
  return res.data.data;
}
