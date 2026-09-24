import { apiClient } from './client';
import type { ApiResponse } from '../types/api';

export interface BenchmarkReportData {
  timestamp: string;
  total_cases: number;
  persisted_cases: number;
  graph_readback_verified: number;
  verification_rate_pct: number;
  sar_generated_count: number;
  avg_latency_s: number;
  cases: Array<{
    case_id: string;
    trigger_type: string;
    status: string;
    verdict: string;
    pattern: string;
    exposure_usd: number;
    writeback_status: string;
    sar_required: boolean;
    approval_route: string;
  }>;
  agent_metrics?: {
    accuracy?: number;
    precision?: number;
    recall?: number;
    f1_score?: number;
    avg_latency_s?: number;
    avg_tool_calls_per_case?: number;
    policy_validation_success_pct?: number;
    [key: string]: any;
  };
}

export async function fetchBenchmarkReport(): Promise<BenchmarkReportData> {
  const res = await apiClient.get<ApiResponse<BenchmarkReportData>>('/api/benchmark');
  return res.data.data;
}
