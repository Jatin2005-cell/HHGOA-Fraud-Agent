import React, { useState } from 'react';
import type { DynamicCase } from '../../types/case';
import { approveAction, rejectAction } from '../../api/approvals';
import { Badge } from '../common/Badge';
import { ShieldCheck, XCircle, CheckCircle2, AlertTriangle, UserCheck } from 'lucide-react';

interface ApprovalTabProps {
  caseData: DynamicCase;
  onRefresh?: () => void;
}

export const ApprovalTab: React.FC<ApprovalTabProps> = ({ caseData, onRefresh }) => {
  const [approverRole, setApproverRole] = useState<'TEAM_LEAD' | 'FRAUD_MANAGER'>(
    caseData.approval_route === 'L2' ? 'FRAUD_MANAGER' : 'TEAM_LEAD'
  );
  const [approverId, setApproverId] = useState('supervisor_ops_01');
  const [decisionReason, setDecisionReason] = useState(
    'Confirmed multi-hop fraud indicators and compliance policy R1-R10 mandates.'
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resultMsg, setResultMsg] = useState<{ success: boolean; text: string } | null>(null);

  const isPending = caseData.approval_status === 'PENDING' || caseData.status === 'APPROVAL_PENDING';
  const isApproved = caseData.approval_status === 'APPROVED';
  const isRejected = caseData.approval_status === 'REJECTED';

  const handleDecision = async (decision: 'APPROVE' | 'REJECT') => {
    setIsSubmitting(true);
    setResultMsg(null);
    try {
      if (decision === 'APPROVE') {
        await approveAction(caseData.case_id, {
          decision: 'APPROVE',
          approver_role: approverRole,
          approver_id: approverId,
          reason: decisionReason,
        });
        setResultMsg({ success: true, text: `Case ${caseData.case_id} action approved successfully.` });
      } else {
        await rejectAction(caseData.case_id, {
          decision: 'REJECT',
          approver_role: approverRole,
          approver_id: approverId,
          reason: decisionReason,
        });
        setResultMsg({ success: true, text: `Case ${caseData.case_id} action rejected.` });
      }
      if (onRefresh) onRefresh();
    } catch (err: any) {
      setResultMsg({ success: false, text: err.message || 'Approval decision rejected by policy guard.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 text-left">
      {/* Approval Status Header */}
      <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-[10px] uppercase font-bold text-slate-400">Governance Tier</span>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-lg font-bold text-slate-900 font-mono">
              Tier {caseData.approval_route.toUpperCase()}
            </span>
            <span className="text-xs text-slate-500">
              ({caseData.approval_route === 'L2' ? 'Fraud Manager Authorization Required' : 'Team Lead Approval'})
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Badge
            label={`Workflow Status: ${caseData.approval_status}`}
            variant={isApproved ? 'green' : isPending ? 'amber' : isRejected ? 'red' : 'slate'}
            size="md"
          />
        </div>
      </div>

      {/* Decision Notification Feedback */}
      {resultMsg && (
        <div
          className={`p-4 rounded-lg border text-xs flex items-center gap-2.5 ${
            resultMsg.success
              ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
              : 'bg-red-50 border-red-200 text-red-900'
          }`}
        >
          {resultMsg.success ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          ) : (
            <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
          )}
          <span>{resultMsg.text}</span>
        </div>
      )}

      {/* Segregation of Duties Notice */}
      <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600 flex items-start gap-3">
        <UserCheck className="w-4 h-4 text-sky-700 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-800">Four-Eyes Governance & Non-Self-Approval: </span>
          The orchestrating AI agent cannot approve its own mitigation recommendations. Human supervisors must review
          the graph context, policy rules, and exposure before granting authorization.
        </div>
      </div>

      {/* Pending Decision Form */}
      {isPending && (
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm space-y-4">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 border-b border-slate-100 pb-2">
            Human Supervisor Authorization Terminal
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Authorizer Role</label>
              <select
                value={approverRole}
                onChange={(e) => setApproverRole(e.target.value as any)}
                className="w-full h-9 px-2.5 bg-slate-50 border border-slate-300 rounded font-mono text-slate-900 focus:outline-none focus:ring-1 focus:ring-sky-500"
              >
                <option value="TEAM_LEAD">TEAM_LEAD (Authorized for L1)</option>
                <option value="FRAUD_MANAGER">FRAUD_MANAGER (Authorized for L1 & L2)</option>
              </select>
              {caseData.approval_route === 'L2' && approverRole !== 'FRAUD_MANAGER' && (
                <p className="text-[11px] text-red-600 mt-1">
                  * L2 action requires FRAUD_MANAGER role per policy.
                </p>
              )}
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Authorizer Staff ID</label>
              <input
                type="text"
                value={approverId}
                onChange={(e) => setApproverId(e.target.value)}
                className="w-full h-9 px-3 bg-slate-50 border border-slate-300 rounded font-mono text-slate-900 focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Supervisory Decision Notes / Audit Justification
            </label>
            <textarea
              rows={3}
              value={decisionReason}
              onChange={(e) => setDecisionReason(e.target.value)}
              className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-sky-500"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button
              onClick={() => handleDecision('REJECT')}
              disabled={isSubmitting}
              className="px-4 py-2 text-xs font-semibold text-red-700 bg-red-50 hover:bg-red-100 border border-red-200 rounded transition-colors inline-flex items-center gap-1.5"
            >
              <XCircle className="w-4 h-4" />
              Reject Mitigation
            </button>
            <button
              onClick={() => handleDecision('APPROVE')}
              disabled={isSubmitting}
              className="px-5 py-2 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-400 rounded transition-colors inline-flex items-center gap-1.5 shadow-sm"
            >
              <ShieldCheck className="w-4 h-4" />
              {isSubmitting ? 'Verifying Authorization...' : 'Authorize Action'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
