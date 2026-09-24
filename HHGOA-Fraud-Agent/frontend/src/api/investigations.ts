import { apiClient } from './client';
import type { ApiResponse } from '../types/api';
import type { DynamicCase, TimelineEvent } from '../types/case';
import type { InvestigationGraph } from '../types/evidence';
import type { CaseActionsResponse } from '../types/action';

export interface CreateInvestigationPayload {
  case_id: string;
  trigger_type: 'risk_score' | 'customer_report' | 'analyst_request' | string;
  trigger_text: string;
  flagged_txn_id: string;
  customer_id: string;
  card_id: string;
  risk_score?: number;
}

export async function createInvestigation(payload: CreateInvestigationPayload): Promise<DynamicCase> {
  const res = await apiClient.post<ApiResponse<DynamicCase>>('/api/investigations', payload);
  return res.data.data;
}

export async function runInvestigation(caseId: string): Promise<any> {
  const res = await apiClient.post<ApiResponse<any>>(`/api/investigations/${encodeURIComponent(caseId)}/run`);
  return res.data.data;
}

export async function fetchInvestigation(caseId: string): Promise<DynamicCase> {
  const res = await apiClient.get<ApiResponse<DynamicCase>>(`/api/investigations/${encodeURIComponent(caseId)}`);
  return res.data.data;
}

export async function fetchInvestigationTimeline(caseId: string): Promise<TimelineEvent[]> {
  const res = await apiClient.get<ApiResponse<TimelineEvent[]>>(
    `/api/investigations/${encodeURIComponent(caseId)}/timeline`
  );
  return res.data.data;
}

export async function fetchInvestigationGraph(caseId: string): Promise<InvestigationGraph> {
  const res = await apiClient.get<ApiResponse<InvestigationGraph>>(
    `/api/investigations/${encodeURIComponent(caseId)}/graph`
  );
  return res.data.data;
}

export async function fetchInvestigationActions(caseId: string): Promise<CaseActionsResponse> {
  const res = await apiClient.get<ApiResponse<CaseActionsResponse>>(
    `/api/investigations/${encodeURIComponent(caseId)}/actions`
  );
  return res.data.data;
}
