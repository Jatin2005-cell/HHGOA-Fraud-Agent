import React from 'react';
import type { DynamicCase } from '../../types/case';
import { formatCurrency, formatPattern } from '../../utils/formatters';
import { formatDateTime } from '../../utils/dates';
import { getVerdictVisual, getLifecycleStatusVisual, getRiskTierVisual } from '../../utils/risk';
import { Badge } from '../common/Badge';
import { ShieldCheck, User, CreditCard, Laptop, Hash, AlertTriangle, Scale } from 'lucide-react';

interface OverviewTabProps {
  caseData: DynamicCase;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({ caseData }) => {
  const verdictVis = getVerdictVisual(caseData.verdict);
  const statusVis = getLifecycleStatusVisual(caseData.status);
  const riskVis = getRiskTierVisual(caseData.risk_score);

  return (
    <div className="space-y-6 text-left">
      {/* Key Metric Tiles */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Dataset Risk Score */}
        <div className="bg-slate-50 border border-slate-200 p-4 rounded-lg">
          <span className="text-[11px] uppercase font-bold text-slate-500 tracking-wider flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
            Dataset Risk Score
          </span>
          <div className="text-xl font-bold font-mono text-slate-900 mt-1">
            {caseData.risk_score !== null && caseData.risk_score !== undefined
              ? caseData.risk_score.toFixed(2)
              : 'N/A'}
          </div>
          <span className="text-[10px] text-slate-500 mt-0.5 block">
            {riskVis.label} (Original Model Inbound)
          </span>
        </div>

        {/* Autonomous Agent Fraud Probability */}
        <div className="bg-sky-50/50 border border-sky-200 p-4 rounded-lg">
          <span className="text-[11px] uppercase font-bold text-sky-800 tracking-wider flex items-center gap-1.5">
            <Scale className="w-3.5 h-3.5 text-sky-600" />
            Agent Fraud Probability
          </span>
          <div className="text-xl font-bold font-mono text-sky-950 mt-1">
            {(caseData.fraud_probability * 100).toFixed(1)}%
          </div>
          <span className="text-[10px] text-sky-700 mt-0.5 block">
            Multi-hop GraphRAG Confidence
          </span>
        </div>

        {/* Financial Exposure */}
        <div className="bg-slate-50 border border-slate-200 p-4 rounded-lg">
          <span className="text-[11px] uppercase font-bold text-slate-500 tracking-wider">
            Total Exposure
          </span>
          <div className="text-xl font-bold text-slate-900 mt-1">
            {formatCurrency(caseData.exposure_usd)}
          </div>
          <span className="text-[10px] text-slate-500 mt-0.5 block">
            Affected Transactions ({caseData.affected_txn_ids?.length || 0})
          </span>
        </div>

        {/* Graph Verification Status */}
        <div className="bg-slate-50 border border-slate-200 p-4 rounded-lg">
          <span className="text-[11px] uppercase font-bold text-slate-500 tracking-wider flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            TigerGraph Writeback
          </span>
          <div className="text-xl font-bold text-emerald-700 mt-1">
            {caseData.graph_verification?.writeback_status || 'VERIFIED'}
          </div>
          <span className="text-[10px] text-slate-500 mt-0.5 block">
            DynamicCase & Incident Edges Intact
          </span>
        </div>
      </div>

      {/* Entity Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Core Case Attributes */}
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 border-b border-slate-100 pb-2">
            Investigation Attributes
          </h4>

          <div className="grid grid-cols-2 gap-y-3 text-xs">
            <div className="text-slate-500">Case Identifier:</div>
            <div className="font-mono font-semibold text-slate-900">{caseData.case_id}</div>

            <div className="text-slate-500">Lifecycle State:</div>
            <div>
              <Badge label={statusVis.label} variant="amber" size="sm" />
            </div>

            <div className="text-slate-500">Final Verdict:</div>
            <div>
              <Badge label={verdictVis.label} variant={caseData.verdict === 'fraud' ? 'red' : 'green'} size="sm" />
            </div>

            <div className="text-slate-500">Fraud Typology:</div>
            <div className="font-medium text-purple-900">{formatPattern(caseData.fraud_pattern)}</div>

            <div className="text-slate-500">Trigger Type:</div>
            <div className="font-mono capitalize text-slate-700">{caseData.trigger_type.replace('_', ' ')}</div>

            <div className="text-slate-500">Created Timestamp:</div>
            <div className="text-slate-700">{formatDateTime(caseData.created_at)}</div>

            <div className="text-slate-500">Stop Reason:</div>
            <div className="text-slate-700 font-mono text-[11px]">{caseData.stop_reason || 'NORMAL_EVALUATION'}</div>
          </div>
        </div>

        {/* Financial & Graph Entities */}
        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 border-b border-slate-100 pb-2">
            Connected Graph Entities
          </h4>

          <div className="space-y-2.5 text-xs">
            <div className="flex items-center justify-between p-2 bg-slate-50 rounded border border-slate-100">
              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-slate-500" />
                <span className="text-slate-600">Customer ID:</span>
              </div>
              <span className="font-mono font-medium text-slate-900">{caseData.customer_id}</span>
            </div>

            <div className="flex items-center justify-between p-2 bg-slate-50 rounded border border-slate-100">
              <div className="flex items-center gap-2">
                <CreditCard className="w-4 h-4 text-slate-500" />
                <span className="text-slate-600">Primary Card ID:</span>
              </div>
              <span className="font-mono font-medium text-slate-900">{caseData.card_id}</span>
            </div>

            <div className="flex items-center justify-between p-2 bg-slate-50 rounded border border-slate-100">
              <div className="flex items-center gap-2">
                <Hash className="w-4 h-4 text-slate-500" />
                <span className="text-slate-600">Flagged Transaction:</span>
              </div>
              <span className="font-mono font-medium text-slate-900">#{caseData.flagged_txn_id}</span>
            </div>

            <div className="flex items-center justify-between p-2 bg-slate-50 rounded border border-slate-100">
              <div className="flex items-center gap-2">
                <Laptop className="w-4 h-4 text-slate-500" />
                <span className="text-slate-600">Connected Devices:</span>
              </div>
              <span className="font-mono text-slate-900">
                {caseData.connected_device_profiles?.length
                  ? caseData.connected_device_profiles.join(', ')
                  : 'None associated'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Note */}
      <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
          Investigation Case Executive Summary
        </h4>
        <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-line bg-slate-50 p-4 rounded border border-slate-200 font-sans">
          {caseData.summary || 'No narrative summary available.'}
        </p>
      </div>
    </div>
  );
};
