import React from 'react';
import type { DynamicCase } from '../../types/case';
import { formatCurrency, formatPattern } from '../../utils/formatters';
import { Sparkles, HelpCircle, CheckCircle, AlertTriangle, ShieldCheck, FileText } from 'lucide-react';

interface AiExplanationTabProps {
  caseData: DynamicCase;
}

export const AiExplanationTab: React.FC<AiExplanationTabProps> = ({ caseData }) => {
  return (
    <div className="space-y-6 text-left">
      <div className="flex items-center gap-2 border-b border-slate-200 pb-3">
        <Sparkles className="w-4 h-4 text-purple-600" />
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
          Structured GraphRAG Intelligence Explanation
        </h4>
        <span className="text-[11px] text-slate-500 ml-auto">
          Generated via multi-hop GSQL query context and historical case memory.
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* 1. Why Flagged */}
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs space-y-1.5">
          <div className="text-[11px] font-bold uppercase tracking-wider text-sky-800 flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5 text-sky-600" />
            1. Why was this case flagged?
          </div>
          <p className="text-xs text-slate-700 leading-relaxed">
            Case initiated via <span className="font-mono font-semibold">{caseData.trigger_type}</span> on transaction{' '}
            <span className="font-mono font-semibold">#{caseData.flagged_txn_id}</span> for card{' '}
            <span className="font-mono font-semibold">{caseData.card_id}</span>. Trigger signal:{' '}
            <span className="italic text-slate-800">&quot;{caseData.trigger_text}&quot;</span>.
          </p>
        </div>

        {/* 2. What Evidence Found */}
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs space-y-1.5">
          <div className="text-[11px] font-bold uppercase tracking-wider text-purple-800 flex items-center gap-1.5">
            <CheckCircle className="w-3.5 h-3.5 text-purple-600" />
            2. What evidence was found?
          </div>
          <p className="text-xs text-slate-700 leading-relaxed">
            Multi-hop TigerGraph traversal discovered{' '}
            <span className="font-semibold">{caseData.affected_txn_ids?.length || 0} affected transactions</span>,{' '}
            <span className="font-semibold">{caseData.connected_card_ids?.length || 0} connected cards</span>, and{' '}
            <span className="font-semibold">{caseData.connected_device_profiles?.length || 0} shared device profiles</span>.
            Total cluster exposure stands at <span className="font-semibold">{formatCurrency(caseData.exposure_usd)}</span>.
          </p>
        </div>

        {/* 3. What Pattern Identified */}
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs space-y-1.5">
          <div className="text-[11px] font-bold uppercase tracking-wider text-red-800 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-red-600" />
            3. What pattern was identified?
          </div>
          <p className="text-xs text-slate-700 leading-relaxed">
            Classified as <span className="font-bold text-red-900">{formatPattern(caseData.fraud_pattern)}</span> with{' '}
            <span className="font-semibold">{(caseData.fraud_probability * 100).toFixed(1)}% probability</span>.{' '}
            {caseData.pattern_description || 'Synthesized based on device collisions and velocity window queries.'}
          </p>
        </div>

        {/* 4. What is Uncertain */}
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs space-y-1.5">
          <div className="text-[11px] font-bold uppercase tracking-wider text-amber-800 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
            4. What is uncertain?
          </div>
          <p className="text-xs text-slate-700 leading-relaxed">
            {caseData.verdict === 'uncertain'
              ? 'Ambiguity remains regarding cardholder authorization vs malicious impersonation. Controlled customer verification step required prior to permanent blocking.'
              : 'Graph density and customer denial corroboration resolve core epistemic uncertainty; no further out-of-band inquiries required.'}
          </p>
        </div>

        {/* 5. What Action is Recommended & Why */}
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs space-y-1.5">
          <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-emerald-600" />
            5. What action is recommended & why?
          </div>
          <p className="text-xs text-slate-700 leading-relaxed">
            Final action: <span className="font-bold">{caseData.final_next_best_action?.[0]?.action || 'DISMISS_ALERT'}</span>.
            Reason:{' '}
            {caseData.final_next_best_action?.[0]?.reason ||
              'Mitigation calibrated to total financial exposure and fraud pattern severity.'}
          </p>
        </div>

        {/* 6. What Policy & Approval Apply */}
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs space-y-1.5">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-slate-600" />
            6. What policy rules & approval apply?
          </div>
          <p className="text-xs text-slate-700 leading-relaxed">
            Governed by Bank Policy Rules R1–R10. Action routed to{' '}
            <span className="font-mono font-bold text-sky-800">{caseData.approval_route.toUpperCase()}</span> tier, requiring{' '}
            <span className="font-semibold">
              {caseData.approval_route === 'L2'
                ? 'Fraud Manager'
                : caseData.approval_route === 'L1'
                ? 'Team Lead'
                : 'Automated Agent'}
            </span>{' '}
            authorization.
          </p>
        </div>
      </div>
    </div>
  );
};
