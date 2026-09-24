export interface ApprovalDecisionRequest {
  decision: 'APPROVE' | 'REJECT';
  approver_role: 'TEAM_LEAD' | 'FRAUD_MANAGER' | 'COMPLIANCE_OFFICER';
  approver_id: string;
  reason: string;
}

export interface PendingApprovalItem {
  case_id: string;
  status: string;
  approval_route: 'L1' | 'L2' | string;
  verdict: string;
  fraud_pattern: string;
  exposure_usd: number;
  risk_score: number | null;
  actions: string[];
  created_at: string;
}
