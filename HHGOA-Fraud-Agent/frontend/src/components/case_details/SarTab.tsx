import React, { useState, useEffect } from 'react';
import { fetchSarByCaseId } from '../../api/sar';
import type { SarRecord } from '../../types/sar';
import { formatCurrency } from '../../utils/formatters';
import { formatDateTime } from '../../utils/dates';
import { Skeleton } from '../common/Skeleton';
import { AlertCircle, Info } from 'lucide-react';

interface SarTabProps {
  caseId: string;
  sarRequired: boolean;
}

export const SarTab: React.FC<SarTabProps> = ({ caseId, sarRequired }) => {
  const [sar, setSar] = useState<SarRecord | null>(null);
  const [isLoading, setIsLoading] = useState(sarRequired);

  useEffect(() => {
    if (!sarRequired) return;
    const loadSar = async () => {
      setIsLoading(true);
      try {
        const data = await fetchSarByCaseId(caseId);
        setSar(data);
      } catch (err) {
        console.error('Failed to load SAR record', err);
      } finally {
        setIsLoading(false);
      }
    };
    loadSar();
  }, [caseId, sarRequired]);

  if (!sarRequired) {
    return (
      <div className="bg-white p-8 rounded-lg border border-slate-200 text-center space-y-2">
        <Info className="w-8 h-8 text-slate-400 mx-auto" />
        <h4 className="text-sm font-semibold text-slate-800">SAR Filing Not Mandated</h4>
        <p className="text-xs text-slate-500 max-w-md mx-auto">
          Under Bank Fraud Policy R10 and FinCEN guidelines, this investigation did not breach statutory filing thresholds
          (exposure under $1,000 without confirmed syndicate or account takeover typologies).
        </p>
      </div>
    );
  }

  if (isLoading) {
    return <Skeleton className="h-64 w-full rounded-lg" />;
  }

  return (
    <div className="space-y-5 text-left">
      {/* Prominent Simulated Hackathon Banner */}
      <div className="p-3 bg-amber-500/10 border border-amber-300 rounded-lg flex items-center justify-between">
        <div className="flex items-center gap-2 text-amber-900 font-semibold text-xs">
          <AlertCircle className="w-4 h-4 text-amber-600" />
          <span>SIMULATED HACKATHON SAR (FINCEN FORM 111 COMPLIANT FORMAT)</span>
        </div>
        <span className="text-[11px] font-mono text-amber-800">Demo Simulation Only &bull; Not Transmitted</span>
      </div>

      {sar ? (
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm space-y-5">
          {/* Header Metadata */}
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400">SAR Reference ID</span>
              <div className="text-base font-mono font-bold text-slate-900">
                {sar.sar_id || `SAR-${caseId}-2026`}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono bg-purple-50 text-purple-700 px-2.5 py-1 rounded border border-purple-200 font-bold">
                STATUS: {sar.filing_status || 'MANDATED'}
              </span>
              <span className="text-[11px] font-mono bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded border border-emerald-200 font-bold">
                EXPOSURE: {formatCurrency(sar.total_exposure_usd)}
              </span>
            </div>
          </div>

          {/* Core Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-3 bg-slate-50 rounded border border-slate-200">
              <span className="text-[10px] font-bold uppercase text-slate-500 block mb-1">Triggering Policy Rule</span>
              <span className="text-slate-800 font-medium">
                {sar.trigger_reason || 'Policy R10 (Exposure >= $1,000 with multi-hop fraud confirmation)'}
              </span>
            </div>

            <div className="p-3 bg-slate-50 rounded border border-slate-200">
              <span className="text-[10px] font-bold uppercase text-slate-500 block mb-1">Activity Period</span>
              <span className="text-slate-800 font-mono">
                {formatDateTime(sar.activity_start_date)} &mdash; {formatDateTime(sar.activity_end_date)}
              </span>
            </div>
          </div>

          {/* Legal Narrative */}
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-2">
              FinCEN Part V: Suspicious Activity Narrative (6&ndash;12 Sentences)
            </span>
            <div className="p-4 bg-slate-50 border border-slate-300 rounded text-xs text-slate-800 leading-relaxed font-mono whitespace-pre-line">
              {sar.narrative || 'Generating legal compliance narrative...'}
            </div>
          </div>

          {/* Subjects Table */}
          {sar.primary_subject && (
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-2">
                Part I: Subject Information
              </span>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded grid grid-cols-3 gap-2 text-xs font-mono">
                <div>
                  <span className="text-[10px] text-slate-400 block uppercase">Customer</span>
                  <span className="text-slate-900 font-bold">{sar.primary_subject.customer_id}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block uppercase">Card Ref</span>
                  <span className="text-slate-900 font-bold">{sar.primary_subject.card_id}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block uppercase">Role</span>
                  <span className="text-slate-900 font-bold">{sar.primary_subject.role}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="p-6 bg-white rounded-lg border border-slate-200 text-center text-xs text-slate-500">
          SAR record queued for generation upon supervisory confirmation.
        </div>
      )}
    </div>
  );
};
