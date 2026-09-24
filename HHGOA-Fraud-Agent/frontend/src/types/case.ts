import type { ProvenanceContract } from './api';

export type CaseStatus =
  | 'NEW'
  | 'INVESTIGATING'
  | 'EVIDENCE_PENDING'
  | 'REVIEW'
  | 'ACTION_REQUIRED'
  | 'APPROVAL_PENDING'
  | 'RESOLVED'
  | 'CLOSED'
  | 'ESCALATED'
  | 'FAILED'
  | 'CANCELLED';

export type CaseVerdict = 'fraud' | 'legitimate' | 'uncertain' | 'CONFIRMED_FRAUD' | 'LEGITIMATE' | 'SUSPICIOUS';

export type ApprovalRoute = 'auto' | 'L1' | 'L2';
export type ApprovalStatus = 'NOT_REQUIRED' | 'PENDING' | 'APPROVED' | 'REJECTED';
export type SarStatus = 'NOT_REQUIRED' | 'GENERATED' | 'REVIEW_REQUIRED';

export interface DynamicCase {
  case_id: string;
  status: CaseStatus;
  created_at: string;
  updated_at: string;
  trigger_type: string;
  trigger_text: string;
  flagged_txn_id: string;
  customer_id: string;
  card_id: string;
  verdict: CaseVerdict | string;
  fraud_probability: number;
  risk_score: number | null;
  fraud_pattern: string;
  pattern_description: string;
  affected_txn_ids: string[];
  exposure_usd: number;
  connected_card_ids: string[];
  connected_device_profiles: string[];
  similar_prior_cases?: string[];
  approval_route: ApprovalRoute | string;
  approval_status: ApprovalStatus | string;
  sar_required: boolean;
  sar_status: SarStatus | string;
  summary: string;
  stop_reason: string;
  evidence?: any[];
  evidence_requests?: any[];
  initial_next_best_action?: any[];
  final_next_best_action?: any[];
  initial_actions?: any[];
  final_actions?: any[];
  what_changed?: string;
  timeline?: TimelineEvent[];
  provenance?: ProvenanceContract;
  graph_verification?: {
    writeback_status: string;
    case_vertex_exists: boolean;
    incident_edge_count: number;
  };
}

export interface CaseListResponse {
  items: DynamicCase[];
  total: number;
  page: number;
  page_size: number;
}

export interface TimelineEvent {
  timestamp: string;
  actor: string;
  event_type: string;
  description: string;
  tool?: string;
  evidence_ref?: string;
}
