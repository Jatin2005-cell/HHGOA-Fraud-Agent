export interface NextBestAction {
  action: string;
  route: 'auto' | 'L1' | 'L2' | string;
  policy_rule: string;
  reason: string;
  required_role?: string;
  status?: string;
}

export interface CaseActionsResponse {
  case_id: string;
  initial_next_best_action: NextBestAction[];
  final_next_best_action: NextBestAction[];
  what_changed: string;
  approval_route: string;
  approval_status: string;
}
