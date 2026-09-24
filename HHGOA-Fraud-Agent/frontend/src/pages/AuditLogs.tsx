import React, { useState, useEffect } from 'react';
import {
  ScrollText,
  Search,
  Filter,
  RefreshCw,
  User,
  FileCode,
  ChevronLeft,
  ChevronRight,
  Eye,
  X,
  Lock,
} from 'lucide-react';
import { fetchAuditLogs } from '../api/audit';
import type { AuditLogItem } from '../api/audit';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Skeleton } from '../components/common/Skeleton';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { formatDateTime } from '../utils/dates';

export const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(25);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [caseFilter, setCaseFilter] = useState('');
  const [opFilter, setOpFilter] = useState('');
  const [selectedEntry, setSelectedEntry] = useState<AuditLogItem | null>(null);

  const loadData = async (currentPage = page) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchAuditLogs({
        case_id: caseFilter || undefined,
        operation: opFilter || undefined,
        page: currentPage,
        page_size: pageSize,
      });
      setLogs(res.items || []);
      setTotal(res.total || 0);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve immutable audit trail.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(1);
  }, [caseFilter, opFilter]);

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    loadData(newPage);
  };

  const sanitizeDetails = (details: Record<string, any>) => {
    if (!details) return {};
    const sanitized = { ...details };
    const sensitiveKeys = ['password', 'secret', 'token', 'key', 'auth', 'cookie'];
    for (const k of Object.keys(sanitized)) {
      if (sensitiveKeys.some((s) => k.toLowerCase().includes(s))) {
        sanitized[k] = '[REDACTED_SECRET]';
      }
    }
    return sanitized;
  };

  const getStatusBadge = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'success':
      case 'completed':
      case 'approved':
        return <Badge label={status.toUpperCase()} variant="green" size="sm" />;
      case 'rejected':
      case 'failed':
      case 'escalated':
        return <Badge label={status.toUpperCase()} variant="red" size="sm" />;
      case 'pending':
        return <Badge label="PENDING" variant="amber" size="sm" />;
      default:
        return <Badge label={status?.toUpperCase() || 'INFO'} variant="blue" size="sm" />;
    }
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="space-y-6 text-left">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <ScrollText className="w-5 h-5 text-sky-600" />
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              Governance & Security Audit Trail
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Immutable log of all investigation actions, agent tool calls, approval authorizations, and writebacks
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 bg-slate-100 px-3 py-1.5 rounded-md border border-slate-200">
            <Lock className="w-3.5 h-3.5 text-slate-600" />
            <span>Tamper-Resistant Append-Only Log</span>
          </div>
          <button
            onClick={() => loadData(page)}
            disabled={loading}
            className="px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 rounded-md transition-colors shadow-sm inline-flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter by Case ID..."
              value={caseFilter}
              onChange={(e) => setCaseFilter(e.target.value)}
              className="pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-sky-500 w-48 text-slate-800"
            />
          </div>

          <div className="relative">
            <Filter className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter by Operation / Tool..."
              value={opFilter}
              onChange={(e) => setOpFilter(e.target.value)}
              className="pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-md focus:outline-none focus:ring-1 focus:ring-sky-500 w-56 text-slate-800"
            />
          </div>

          {(caseFilter || opFilter) && (
            <button
              onClick={() => {
                setCaseFilter('');
                setOpFilter('');
              }}
              className="text-xs text-sky-600 hover:text-sky-800 font-medium"
            >
              Clear filters
            </button>
          )}
        </div>

        <div className="text-xs text-slate-500">
          Showing <strong>{logs.length}</strong> of <strong>{total}</strong> audit events
        </div>
      </div>

      {/* Audit Log Table */}
      <Card
        title="Audit Events"
        subtitle="Chronological sequence with verified cryptographic trace"
      >
        {error ? (
          <ErrorState message={error} onRetry={() => loadData(page)} />
        ) : loading ? (
          <div className="space-y-2 py-4">
            {Array.from({ length: 10 }).map((_, i) => (
              <Skeleton key={i} className="h-10 rounded" />
            ))}
          </div>
        ) : logs.length === 0 ? (
          <EmptyState
            title="No audit events found"
            description="Try clearing your filters or running an investigation to generate audit events."
          />
        ) : (
          <div>
            <div className="overflow-x-auto -mx-5 -mb-5">
              <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider">
                  <tr>
                    <th className="py-2.5 px-4">Timestamp</th>
                    <th className="py-2.5 px-4">Actor</th>
                    <th className="py-2.5 px-4">Operation</th>
                    <th className="py-2.5 px-4">Case ID</th>
                    <th className="py-2.5 px-4">Status</th>
                    <th className="py-2.5 px-4">Provenance</th>
                    <th className="py-2.5 px-4 text-right">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {logs.map((item, idx) => (
                    <tr
                      key={item.request_id || idx}
                      className="hover:bg-slate-50 transition-colors"
                    >
                      <td className="py-2.5 px-4 font-mono text-slate-600 whitespace-nowrap">
                        {formatDateTime(item.timestamp)}
                      </td>
                      <td className="py-2.5 px-4">
                        <div className="flex items-center gap-1.5 font-medium text-slate-700">
                          <User className="w-3.5 h-3.5 text-slate-400" />
                          <span>{item.actor || 'system'}</span>
                        </div>
                      </td>
                      <td className="py-2.5 px-4 font-mono text-[11px] text-slate-800">
                        <span className="bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded border border-slate-200">
                          {item.operation || 'AUDIT_RECORD'}
                        </span>
                      </td>
                      <td className="py-2.5 px-4 font-mono font-semibold text-sky-700">
                        {item.case_id || 'SYSTEM'}
                      </td>
                      <td className="py-2.5 px-4">
                        {getStatusBadge(item.status || 'SUCCESS')}
                      </td>
                      <td className="py-2.5 px-4">
                        <span className="text-[11px] font-mono text-slate-600">
                          {item.details?.provenance || item.details?.execution_mode || 'OFFLINE_SIM'}
                        </span>
                      </td>
                      <td className="py-2.5 px-4 text-right">
                        <button
                          onClick={() => setSelectedEntry(item)}
                          className="inline-flex items-center gap-1 text-sky-600 hover:text-sky-800 font-medium"
                          title="View sanitized payload"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center justify-between border-t border-slate-200 px-4 py-3 mt-5 -mx-5 bg-slate-50">
              <div className="text-xs text-slate-600">
                Page <strong>{page}</strong> of <strong>{totalPages}</strong>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handlePageChange(page - 1)}
                  disabled={page <= 1}
                  className="px-2.5 py-1 text-xs border border-slate-300 rounded bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-50 inline-flex items-center gap-1"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>Previous</span>
                </button>
                <button
                  onClick={() => handlePageChange(page + 1)}
                  disabled={page >= totalPages}
                  className="px-2.5 py-1 text-xs border border-slate-300 rounded bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-50 inline-flex items-center gap-1"
                >
                  <span>Next</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Detail Inspector Modal */}
      {selectedEntry && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4 backdrop-blur-xs animate-fade-in">
          <div className="bg-white rounded-xl shadow-2xl border border-slate-200 w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden">
            {/* Modal Header */}
            <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-2">
                <FileCode className="w-4 h-4 text-sky-600" />
                <h3 className="text-sm font-bold text-slate-900">
                  Audit Entry Details & Sanitize Trace
                </h3>
              </div>
              <button
                onClick={() => setSelectedEntry(null)}
                className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-5 overflow-y-auto space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded-md border border-slate-200">
                <div>
                  <span className="text-slate-500 block text-[11px]">Request ID:</span>
                  <span className="font-mono text-slate-800 font-medium">
                    {selectedEntry.request_id || 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[11px]">Case ID:</span>
                  <span className="font-mono text-sky-700 font-semibold">
                    {selectedEntry.case_id || 'SYSTEM'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[11px]">Actor:</span>
                  <span className="font-medium text-slate-800">
                    {selectedEntry.actor}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[11px]">Operation:</span>
                  <span className="font-mono text-slate-800">
                    {selectedEntry.operation}
                  </span>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-semibold text-slate-700 uppercase tracking-wider text-[11px]">
                    Payload & Evidence (Secrets Redacted)
                  </span>
                  <span className="text-[10px] text-slate-500 italic">Zero Token/Key Disclosure</span>
                </div>
                <pre className="bg-slate-900 text-slate-100 p-3 rounded-md font-mono text-[11px] overflow-x-auto max-h-72 border border-slate-800">
                  {JSON.stringify(sanitizeDetails(selectedEntry.details), null, 2)}
                </pre>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-5 py-3 border-t border-slate-200 bg-slate-50 flex justify-end">
              <button
                onClick={() => setSelectedEntry(null)}
                className="px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-300 hover:bg-slate-100 rounded-md transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
