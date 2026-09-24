import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckSquare, UserCheck, XCircle, CheckCircle, RefreshCw } from 'lucide-react';
import { fetchCases } from '../api/cases';
import { approveAction, rejectAction } from '../api/approvals';
import type { DynamicCase } from '../types/case';
import { Badge } from '../components/common/Badge';
import { Skeleton } from '../components/common/Skeleton';
import { ErrorState } from '../components/common/ErrorState';
import { formatCurrency, formatPattern } from '../utils/formatters';

export const Approvals: React.FC = () => {
  const navigate = useNavigate();
  const [pendingCases, setPendingCases] = useState<DynamicCase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  // Form states for approval dialog
  const [selectedCase, setSelectedCase] = useState<DynamicCase | null>(null);
  const [approverRole, setApproverRole] = useState<'FRAUD_MANAGER' | 'TEAM_LEAD' | 'COMPLIANCE_OFFICER'>('FRAUD_MANAGER');
  const [approverId, setApproverId] = useState('MGR-8841');
  const [decisionReason, setDecisionReason] = useState('Authorized based on verified multi-card syndicate evidence and high exposure.');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadPendingCases = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetchCases({ page: 1, page_size: 50 });
      // Filter cases needing approval or with L1/L2 route
      const filtered = (res.items || []).filter(
        (c) => c.approval_route === 'L1' || c.approval_route === 'L2' || c.status === 'APPROVAL_PENDING'
      );
      setPendingCases(filtered);
    } catch (err: any) {
      setError(err.message || 'Failed to load governance approval queue.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPendingCases();
  }, []);

  const handleApprove = async (caseId: string) => {
    setIsSubmitting(true);
    setActionMessage(null);
    try {
      await approveAction(caseId, {
        decision: 'APPROVE',
        approver_role: approverRole,
        approver_id: approverId,
        reason: decisionReason,
      });
      setActionMessage(`Case ${caseId} successfully approved by ${approverRole}. Status transitioned to RESOLVED.`);
      setSelectedCase(null);
      loadPendingCases();
    } catch (err: any) {
      setActionMessage(`Approval failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async (caseId: string) => {
    setIsSubmitting(true);
    setActionMessage(null);
    try {
      await rejectAction(caseId, {
        decision: 'REJECT',
        approver_role: approverRole,
        approver_id: approverId,
        reason: decisionReason || 'Rejected pending further customer contact verification.',
      });
      setActionMessage(`Case ${caseId} recommendation rejected.`);
      setSelectedCase(null);
      loadPendingCases();
    } catch (err: any) {
      setActionMessage(`Rejection failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 text-left">
      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              Governance & Human Authorization Queue
            </h1>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold border border-amber-300">
              {pendingCases.length} Escalations Pending
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Two-tier human-in-the-loop authorization pipeline enforcing Bank Policy Rules R1–R10.
          </p>
        </div>

        <button
          onClick={loadPendingCases}
          className="p-2 text-slate-500 hover:text-slate-800 bg-white border border-slate-200 rounded-md hover:bg-slate-50 shadow-sm transition-colors"
          title="Refresh Queue"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {actionMessage && (
        <div className="p-3 bg-sky-50 border border-sky-200 rounded-lg text-xs text-sky-900 flex items-center justify-between">
          <span>{actionMessage}</span>
          <button onClick={() => setActionMessage(null)} className="text-sky-600 hover:text-sky-800 font-bold ml-4">
            &times;
          </button>
        </div>
      )}

      {error ? (
        <ErrorState message={error} onRetry={loadPendingCases} />
      ) : isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full rounded-lg" />
          ))}
        </div>
      ) : pendingCases.length === 0 ? (
        <div className="p-12 text-center text-slate-500 text-xs bg-white rounded-lg border border-slate-200">
          <CheckSquare className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-75" />
          <span className="font-semibold block text-slate-700">Governance Queue Clear</span>
          No high-exposure L1 or L2 cases currently awaiting approval.
        </div>
      ) : (
        <div className="space-y-4">
          {pendingCases.map((c) => {
            const isApproved = c.approval_status === 'APPROVED';
            return (
              <div
                key={c.case_id}
                className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm hover:border-slate-300 transition-all text-xs flex flex-col md:flex-row justify-between gap-4"
              >
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-sky-700 text-sm">{c.case_id}</span>
                    <Badge label={`Route: ${c.approval_route}`} variant={c.approval_route === 'L2' ? 'red' : 'amber'} size="sm" />
                    <Badge label={`Status: ${c.approval_status}`} variant={isApproved ? 'green' : 'slate'} size="sm" />
                    <span className="text-slate-400">&bull;</span>
                    <span className="text-slate-600 font-medium">Trigger: {c.trigger_type}</span>
                  </div>

                  <p className="text-slate-700 text-xs leading-relaxed">{c.summary}</p>

                  <div className="flex flex-wrap gap-4 text-[11px] text-slate-500 pt-1">
                    <span>Card: <strong className="text-slate-700 font-mono">{c.card_id}</strong></span>
                    <span>Customer: <strong className="text-slate-700 font-mono">{c.customer_id}</strong></span>
                    <span>Exposure: <strong className="text-slate-700">{formatCurrency(c.exposure_usd)}</strong></span>
                    <span>Pattern: <strong className="text-slate-700">{formatPattern(c.fraud_pattern)}</strong></span>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row items-end md:items-center gap-2 shrink-0">
                  <button
                    onClick={() => navigate(`/cases/${c.case_id}`)}
                    className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900 border border-slate-200 rounded-md hover:bg-slate-50 transition-colors"
                  >
                    View Dossier
                  </button>
                  {!isApproved && (
                    <button
                      onClick={() => {
                        setSelectedCase(c);
                        setApproverRole(c.approval_route === 'L2' ? 'FRAUD_MANAGER' : 'TEAM_LEAD');
                      }}
                      className="px-3.5 py-1.5 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-md transition-colors shadow-sm inline-flex items-center gap-1.5"
                    >
                      <UserCheck className="w-3.5 h-3.5" />
                      <span>Review & Authorize</span>
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Authorization Modal Dialog */}
      {selectedCase && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-white rounded-xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 space-y-4 text-xs">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Authorize Governance Decision: {selectedCase.case_id}
                </h3>
                <span className="text-[11px] text-slate-500">
                  Route: {selectedCase.approval_route} (Mandates {selectedCase.approval_route === 'L2' ? 'FRAUD_MANAGER' : 'TEAM_LEAD'})
                </span>
              </div>
              <button onClick={() => setSelectedCase(null)} className="text-slate-400 hover:text-slate-700 font-bold text-base">
                &times;
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                  Approver Role
                </label>
                <select
                  value={approverRole}
                  onChange={(e: any) => setApproverRole(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-md text-xs font-semibold"
                >
                  <option value="FRAUD_MANAGER">FRAUD_MANAGER (L2 Authorized)</option>
                  <option value="TEAM_LEAD">TEAM_LEAD (L1 Authorized)</option>
                  <option value="COMPLIANCE_OFFICER">COMPLIANCE_OFFICER</option>
                </select>
              </div>

              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                  Operator Identifier
                </label>
                <input
                  type="text"
                  value={approverId}
                  onChange={(e) => setApproverId(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-md text-xs font-mono"
                  placeholder="e.g. MGR-8841"
                />
              </div>

              <div>
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                  Audit Sign-Off Justification
                </label>
                <textarea
                  value={decisionReason}
                  onChange={(e) => setDecisionReason(e.target.value)}
                  rows={3}
                  className="w-full p-2 border border-slate-300 rounded-md text-xs leading-relaxed"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 border-t border-slate-100 pt-3">
              <button
                onClick={() => setSelectedCase(null)}
                className="px-3 py-1.5 rounded-md border border-slate-200 text-slate-600 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={() => handleReject(selectedCase.case_id)}
                disabled={isSubmitting}
                className="px-3.5 py-1.5 rounded-md bg-rose-600 hover:bg-rose-700 text-white font-semibold flex items-center gap-1.5"
              >
                <XCircle className="w-3.5 h-3.5" />
                <span>Reject</span>
              </button>
              <button
                onClick={() => handleApprove(selectedCase.case_id)}
                disabled={isSubmitting}
                className="px-3.5 py-1.5 rounded-md bg-emerald-600 hover:bg-emerald-700 text-white font-semibold flex items-center gap-1.5"
              >
                <CheckCircle className="w-3.5 h-3.5" />
                <span>Approve & Resolve</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
