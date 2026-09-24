/**
 * Runtime Provenance Contract Utility
 * Single authoritative type definitions and helpers for provenance tracking.
 */

export interface RuntimeProvenance {
  execution_mode: 'OFFLINE_STAGED_SIMULATION' | 'LIVE_TIGERGRAPH';
  graph_backend: 'STAGED_DATASET' | 'FraudInvestigationGraph' | null;
  graph_verified: boolean;
  schema_verified: boolean;
  mcp_verified: boolean;
  writeback_verified: boolean;
  evidence_provenance: 'LOCAL_STAGED_DATASET' | 'TIGERGRAPH' | null;
}

export const DEFAULT_OFFLINE_PROVENANCE: RuntimeProvenance = {
  execution_mode: 'OFFLINE_STAGED_SIMULATION',
  graph_backend: 'STAGED_DATASET',
  graph_verified: false,
  schema_verified: false,
  mcp_verified: false,
  writeback_verified: false,
  evidence_provenance: 'LOCAL_STAGED_DATASET',
};

export function isLiveMode(provenance: RuntimeProvenance | null | undefined): boolean {
  return provenance?.execution_mode === 'LIVE_TIGERGRAPH';
}

export function formatExecutionMode(mode: string | undefined): string {
  if (mode === 'LIVE_TIGERGRAPH') return 'Live TigerGraph Engine';
  return 'Offline Staged Simulation';
}

export function formatEvidenceOrigin(origin: string | undefined): string {
  if (origin === 'TIGERGRAPH') return 'TigerGraph RESTPP Cluster';
  return 'Genuine HHGOA_IEEE Staged Dataset (dataset/processed/)';
}
