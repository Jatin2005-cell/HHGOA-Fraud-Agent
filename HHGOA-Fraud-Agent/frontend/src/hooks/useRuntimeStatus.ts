import { useState, useEffect } from 'react';
import { getDependencyHealth } from '../api/health';
import type { RuntimeProvenance } from '../utils/provenance';
import { DEFAULT_OFFLINE_PROVENANCE } from '../utils/provenance';

export interface RuntimeStatusHookResult {
  provenance: RuntimeProvenance;
  status: string;
  dependencies: Record<string, string>;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useRuntimeStatus(pollIntervalMs = 20000): RuntimeStatusHookResult {
  const [provenance, setProvenance] = useState<RuntimeProvenance>(DEFAULT_OFFLINE_PROVENANCE);
  const [status, setStatus] = useState<string>('healthy');
  const [dependencies, setDependencies] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      const res = await getDependencyHealth();
      const prov: RuntimeProvenance = {
        execution_mode: res.data_mode === 'LIVE_TIGERGRAPH' ? 'LIVE_TIGERGRAPH' : 'OFFLINE_STAGED_SIMULATION',
        graph_backend: res.graph_name ? (res.graph_name as any) : 'STAGED_DATASET',
        graph_verified: Boolean(res.graph_verified),
        schema_verified: Boolean(res.schema_verified),
        mcp_verified: Boolean(res.mcp_verified),
        writeback_verified: Boolean(res.writeback_verified),
        evidence_provenance: res.data_mode === 'LIVE_TIGERGRAPH' ? 'TIGERGRAPH' : 'LOCAL_STAGED_DATASET',
      };
      setProvenance(prov);
      setStatus(res.status || 'healthy');
      setDependencies(res.dependencies || {});
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Unable to reach backend /health/dependencies');
      setProvenance(DEFAULT_OFFLINE_PROVENANCE);
      setStatus('degraded');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, pollIntervalMs);
    return () => clearInterval(interval);
  }, [pollIntervalMs]);

  return {
    provenance,
    status,
    dependencies,
    isLoading,
    error,
    refresh: fetchStatus,
  };
}
