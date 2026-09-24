export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  } | null;
  request_id?: string;
  message?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  service: string;
  timestamp?: string;
}

export interface ProvenanceContract {
  execution_mode: 'LIVE_TIGERGRAPH' | 'OFFLINE_STAGED_SIMULATION';
  graph_backend: string | null;
  graph_verified: boolean;
  schema_verified?: boolean;
  mcp_verified: boolean;
  writeback_verified: boolean;
  evidence_provenance: 'TIGERGRAPH' | 'LOCAL_STAGED_DATASET';
}

export interface HealthDependenciesResponse {
  status: string;
  data_mode: 'LIVE_TIGERGRAPH' | 'OFFLINE_STAGED_SIMULATION';
  graph_name: string | null;
  graph_verified: boolean;
  schema_verified: boolean;
  mcp_verified: boolean;
  writeback_verified: boolean;
  dependencies: {
    tigergraph_engine: string;
    mcp_server: string;
    case_management_store: string;
    investigation_agent: string;
  };
}

export interface SearchResult {
  query: string;
  cases: Array<{
    case_id: string;
    verdict: string;
    pattern: string;
    status: string;
    exposure_usd: number;
  }>;
  customers: Array<{
    customer_id: string;
    related_case: string;
    verdict: string;
  }>;
  cards: Array<{
    card_id: string;
    related_case: string;
    customer_id: string;
  }>;
  transactions: Array<{
    transaction_id: string;
    related_case: string;
    card_id: string;
    is_flagged: boolean;
  }>;
  total_matches: number;
}
