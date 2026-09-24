import { apiClient } from './client';
import type { ApiResponse } from '../types/api';
import type { ApprovalDecisionRequest } from '../types/approval';

export async function approveAction(caseId: string, payload: ApprovalDecisionRequest): Promise<any> {
  const res = await apiClient.post<ApiResponse<any>>(
    `/api/approvals/${encodeURIComponent(caseId)}/approve`,
    payload
  );
  return res.data.data;
}

export async function rejectAction(caseId: string, payload: ApprovalDecisionRequest): Promise<any> {
  const res = await apiClient.post<ApiResponse<any>>(
    `/api/approvals/${encodeURIComponent(caseId)}/reject`,
    payload
  );
  return res.data.data;
}
