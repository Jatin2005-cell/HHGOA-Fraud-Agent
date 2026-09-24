import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, ShieldAlert } from 'lucide-react';
import type { DynamicCase } from '../../types/case';
import { Badge } from '../common/Badge';
import { getVerdictVisual, getLifecycleStatusVisual, getRiskTierVisual } from '../../utils/risk';
import { formatCurrency, formatPattern } from '../../utils/formatters';
import { formatDateTime } from '../../utils/dates';

interface CaseTableProps {
  cases: DynamicCase[];
  isLoading?: boolean;
}

export const CaseTable: React.FC<CaseTableProps> = ({ cases, isLoading = false }) => {
  const navigate = useNavigate();

  if (cases.length === 0 && !isLoading) {
    return (
      <div className="py-12 text-center text-slate-500 text-xs bg-white rounded-lg border border-slate-200">
        No fraud cases match the selected filter criteria.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-sm">
      <div className="overflow-x-auto custom-scrollbar">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider text-[11px]">
              <th className="py-3 px-4">Case ID</th>
              <th className="py-3 px-4">Created</th>
              <th className="py-3 px-4">Trigger</th>
              <th className="py-3 px-4">Customer</th>
              <th className="py-3 px-4">Txn ID</th>
              <th className="py-3 px-4">Risk / Prob</th>
              <th className="py-3 px-4">Verdict & Pattern</th>
              <th className="py-3 px-4">Exposure</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Approval</th>
              <th className="py-3 px-4">SAR</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {cases.map((c) => {
              const verdictVis = getVerdictVisual(c.verdict);
              const statusVis = getLifecycleStatusVisual(c.status);
              const riskVis = getRiskTierVisual(c.risk_score ?? c.fraud_probability);

              return (
                <tr
                  key={c.case_id}
                  className="hover:bg-slate-50/80 transition-colors cursor-pointer group"
                  onClick={() => navigate(`/cases/${c.case_id}`)}
                >
                  {/* Case ID */}
                  <td className="py-3 px-4 font-mono font-medium text-sky-700 group-hover:text-sky-900 flex items-center gap-1.5">
                    <ShieldAlert className="w-3.5 h-3.5 text-slate-400 group-hover:text-sky-600" />
                    {c.case_id}
                  </td>

                  {/* Created */}
                  <td className="py-3 px-4 text-slate-500 whitespace-nowrap">
                    {formatDateTime(c.created_at)}
                  </td>

                  {/* Trigger */}
                  <td className="py-3 px-4">
                    <span className="capitalize px-1.5 py-0.5 bg-slate-100 rounded text-[10px] font-mono text-slate-600">
                      {c.trigger_type.replace('_', ' ')}
                    </span>
                  </td>

                  {/* Customer */}
                  <td className="py-3 px-4 font-mono text-slate-800">{c.customer_id}</td>

                  {/* Txn ID */}
                  <td className="py-3 px-4 font-mono text-slate-600">#{c.flagged_txn_id}</td>

                  {/* Risk / Prob */}
                  <td className="py-3 px-4">
                    <div className="flex flex-col gap-0.5">
                      <span className="font-semibold text-slate-900">
                        {riskVis.label}
                      </span>
                      <span className="text-[10px] text-slate-500">
                        Prob: {(c.fraud_probability * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>

                  {/* Verdict & Pattern */}
                  <td className="py-3 px-4">
                    <div className="flex flex-col gap-1">
                      <Badge
                        label={verdictVis.label}
                        variant={
                          verdictVis.label.includes('FRAUD')
                            ? 'red'
                            : verdictVis.label.includes('LEGIT')
                            ? 'green'
                            : 'amber'
                        }
                        size="sm"
                      />
                      <span className="text-[10px] text-slate-500 truncate max-w-[130px]">
                        {formatPattern(c.fraud_pattern)}
                      </span>
                    </div>
                  </td>

                  {/* Exposure */}
                  <td className="py-3 px-4 font-semibold text-slate-900 whitespace-nowrap">
                    {formatCurrency(c.exposure_usd)}
                  </td>

                  {/* Status */}
                  <td className="py-3 px-4">
                    <Badge
                      label={statusVis.label}
                      variant={
                        c.status === 'RESOLVED' || c.status === 'CLOSED'
                          ? 'green'
                          : c.status === 'APPROVAL_PENDING'
                          ? 'amber'
                          : 'blue'
                      }
                      size="sm"
                    />
                  </td>

                  {/* Approval */}
                  <td className="py-3 px-4">
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        c.approval_route === 'L2'
                          ? 'bg-red-50 text-red-700 border border-red-200'
                          : c.approval_route === 'L1'
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {c.approval_route.toUpperCase()}
                    </span>
                  </td>

                  {/* SAR */}
                  <td className="py-3 px-4">
                    {c.sar_required ? (
                      <span className="text-[10px] font-bold px-1.5 py-0.5 bg-purple-50 text-purple-700 border border-purple-200 rounded">
                        MANDATED
                      </span>
                    ) : (
                      <span className="text-[10px] text-slate-400">None</span>
                    )}
                  </td>

                  {/* Actions */}
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/cases/${c.case_id}`);
                      }}
                      className="p-1 text-slate-400 hover:text-sky-700 rounded hover:bg-sky-50 transition-colors inline-flex items-center gap-1 text-[11px] font-medium"
                      title="View Case Details"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Details</span>
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
