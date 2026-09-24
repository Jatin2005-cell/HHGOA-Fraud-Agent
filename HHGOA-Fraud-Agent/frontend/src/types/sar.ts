export interface SarRecord {
  case_id: string;
  sar_id?: string;
  filing_status?: 'MANDATED' | 'DRAFTED' | 'FILED' | 'NOT_REQUIRED';
  status?: string;
  trigger_reason?: string;
  reason?: string;
  total_exposure_usd?: number;
  total_amount_usd?: number;
  activity_start_date?: string;
  activity_end_date?: string;
  activity_dates?: { start?: string; end?: string };
  primary_subject?: {
    customer_id?: string;
    card_id?: string;
    role?: string;
  };
  subjects?: Array<{
    customer_id?: string;
    card_id?: string;
    role?: string;
  }>;
  narrative: string;
  law_enforcement_referral_recommended?: boolean;
  filing_timestamp?: string;
  evidence_references?: string[];
  file?: boolean;
}
