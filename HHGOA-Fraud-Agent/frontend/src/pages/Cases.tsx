import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, RefreshCw } from 'lucide-react';
import { fetchCases } from '../api/cases';
import type { CaseFilterParams } from '../api/cases';
import type { DynamicCase } from '../types/case';
import { CaseTable } from '../components/cases/CaseTable';
import { CaseFilterBar } from '../components/cases/CaseFilterBar';
import { ErrorState } from '../components/common/ErrorState';

export const Cases: React.FC = () => {
  const navigate = useNavigate();
  const [cases, setCases] = useState<DynamicCase[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<CaseFilterParams>({
    page: 1,
    page_size: 25,
  });

  const loadCases = async (currentFilters = filters) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetchCases(currentFilters);
      setCases(res.items || []);
      setTotalCount(res.total || 0);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch investigation cases.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCases(filters);
  }, [filters]);

  const handleFilterChange = (newFilters: CaseFilterParams) => {
    setFilters((prev) => ({ ...prev, ...newFilters, page: 1 }));
  };

  const handleResetFilters = () => {
    setFilters({ page: 1, page_size: 25 });
  };

  return (
    <div className="space-y-6 text-left">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              Investigation Case Management
            </h1>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-semibold border border-slate-300">
              {totalCount} Total Cases
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Active and resolved DynamicCase vertices stored with graph-backed relationship topology.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => loadCases(filters)}
            disabled={isLoading}
            className="p-2 text-slate-500 hover:text-slate-800 bg-white border border-slate-200 rounded-md hover:bg-slate-50 shadow-sm transition-colors"
            title="Refresh Table"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => navigate('/investigate')}
            className="px-3.5 py-1.5 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-md transition-colors shadow-sm inline-flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Investigation</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <CaseFilterBar filters={filters} onChange={handleFilterChange} onReset={handleResetFilters} />

      {/* Error or Table */}
      {error ? (
        <ErrorState message={error} onRetry={() => loadCases(filters)} />
      ) : (
        <CaseTable cases={cases} isLoading={isLoading} />
      )}
    </div>
  );
};
