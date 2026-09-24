import React from 'react';
import type { NextBestAction } from '../../types/action';
import { Badge } from '../common/Badge';
import { ShieldCheck, AlertOctagon, Scale } from 'lucide-react';

interface ActionsTabProps {
  initialActions?: NextBestAction[];
  finalActions?: NextBestAction[];
  whatChanged?: string;
  approvalRoute: string;
  approvalStatus: string;
}

export const ActionsTab: React.FC<ActionsTabProps> = ({
  initialActions = [],
  finalActions = [],
  whatChanged,
  approvalRoute,
  approvalStatus,
}) => {
  return (
    <div className="space-y-6 text-left">
      {/* Prominent Recommended Action Card */}
      <div className="p-5 rounded-lg border border-sky-200 bg-sky-50/40 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-sky-200 pb-3 mb-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-sky-700" />
            <h4 className="text-sm font-bold text-sky-950 uppercase tracking-tight">
              Recommended Next Best Action (Final Post-GraphRAG)
            </h4>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-600">Approval Tier:</span>
            <Badge
              label={`${approvalRoute.toUpperCase()} (${
                approvalRoute === 'L2' ? 'Fraud Manager' : approvalRoute === 'L1' ? 'Team Lead' : 'Auto-Exec'
              })`}
              variant={approvalRoute === 'L2' ? 'red' : approvalRoute === 'L1' ? 'amber' : 'blue'}
            />
            <Badge
              label={`Status: ${approvalStatus}`}
              variant={approvalStatus === 'APPROVED' ? 'green' : approvalStatus === 'PENDING' ? 'amber' : 'slate'}
            />
          </div>
        </div>

        {finalActions.length > 0 ? (
          <div className="space-y-3">
            {finalActions.map((act, idx) => (
              <div key={idx} className="bg-white p-4 rounded-md border border-slate-200 shadow-xs">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-sm font-bold text-red-700 bg-red-50 px-2 py-0.5 rounded border border-red-200">
                    {act.action}
                  </span>
                  <span className="font-mono text-xs text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
                    Policy: {act.policy_rule || 'R1-R10 Compliance'}
                  </span>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed">{act.reason}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs text-slate-600 italic">No mitigation action required (Legitimate classification).</div>
        )}
      </div>

      {/* Evolution: Initial vs Final Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Initial Action Card */}
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-3">
            <Scale className="w-4 h-4 text-slate-500" />
            <h5 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              1. Initial Action (Single-Hop Signal)
            </h5>
          </div>
          {initialActions.length > 0 ? (
            <div className="space-y-2">
              {initialActions.map((act, idx) => (
                <div key={idx} className="p-3 bg-slate-50 rounded border border-slate-200 text-xs">
                  <div className="font-mono font-bold text-slate-900 mb-1">{act.action}</div>
                  <div className="text-slate-600">{act.reason}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-xs text-slate-400 italic">No initial action proposed.</div>
          )}
        </div>

        {/* What Changed Banner */}
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-3">
            <AlertOctagon className="w-4 h-4 text-purple-600" />
            <h5 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              2. GraphRAG Impact (What Changed?)
            </h5>
          </div>
          <div className="p-3.5 bg-purple-50/50 border border-purple-200 rounded text-xs text-purple-950 leading-relaxed">
            {whatChanged ||
              'Multi-hop TigerGraph traversal and historical case retrieval confirmed cluster density, adjusting escalation tier and SAR filing obligation.'}
          </div>
        </div>
      </div>
    </div>
  );
};
