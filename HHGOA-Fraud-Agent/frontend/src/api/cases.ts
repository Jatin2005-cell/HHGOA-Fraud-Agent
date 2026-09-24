import { apiClient } from './client';
import type { ApiResponse } from '../types/api';
import type { DynamicCase, CaseListResponse } from '../types/case';

export interface CaseFilterParams {
  status?: string;
  pattern?: string;
  customer_id?: string;
  card_id?: string;
  risk_level?: string;
  approval_status?: string;
  sar_status?: string;
  page?: number;
  page_size?: number;
}

export async function fetchCases(params: CaseFilterParams = {}): Promise<CaseListResponse> {
  const res = await apiClient.get<ApiResponse<CaseListResponse>>('/api/cases', {
    params: {
      page: params.page || 1,
      page_size: params.page_size || 20,
      ...(params.status ? { status: params.status } : {}),
      ...(params.pattern ? { pattern: params.pattern } : {}),
      ...(params.customer_id ? { customer_id: params.customer_id } : {}),
      ...(params.card_id ? { card_id: params.card_id } : {}),
      ...(params.risk_level ? { risk_level: params.risk_level } : {}),
      ...(params.approval_status ? { approval_status: params.approval_status } : {}),
      ...(params.sar_status ? { sar_status: params.sar_status } : {}),
    },
  });
  return res.data.data;
}

export async function fetchCaseById(caseId: string): Promise<DynamicCase> {
  const res = await apiClient.get<ApiResponse<DynamicCase>>(`/api/cases/${encodeURIComponent(caseId)}`);
  return res.data.data;
}

export async function fetchDashboardSummary(): Promise<any> {
  const res = await apiClient.get<ApiResponse<any>>('/api/dashboard/summary');
  return res.data.data;
}

export async function fetchDashboardDistributions(): Promise<any> {
  const res = await apiClient.get<ApiResponse<any>>('/api/dashboard/distribution');
  return res.data.data;
}
