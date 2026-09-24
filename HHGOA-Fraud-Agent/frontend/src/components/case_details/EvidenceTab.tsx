import React from 'react';
import type { EvidenceItem } from '../../types/evidence';
import { Badge } from '../common/Badge';
import { ShieldCheck, Database, Wrench, Layers } from 'lucide-react';

interface EvidenceTabProps {
  evidenceList: EvidenceItem[];
}

export const EvidenceTab: React.FC<EvidenceTabProps> = ({ evidenceList }) => {
  if (!evidenceList || evidenceList.length === 0) {
    return (
      <div className="py-12 text-center text-slate-500 text-xs bg-white rounded-lg border border-slate-200">
        No formal evidence items recorded for this investigation.
      </div>
    );
  }

  return (
    <div className="space-y-4 text-left">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
          Provenanced Graph & Behavioral Evidence ({evidenceList.length} Items)
        </h4>
        <span className="text-[11px] text-slate-500">
          All evidence items originate from verified TigerGraph GSQL queries & MCP tools.
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {evidenceList.map((ev, idx) => {
          const status = ev.epistemic_status || 'OBSERVED';
          const isObserved = status === 'OBSERVED';
          const isUncertainty = status === 'UNCERTAINTY';

          return (
            <div
              key={idx}
              className={`p-4 rounded-lg border shadow-sm transition-all bg-white ${
                isObserved
                  ? 'border-slate-200 hover:border-sky-300'
                  : isUncertainty
                  ? 'border-amber-200 bg-amber-50/20'
                  : 'border-purple-200 bg-purple-50/20'
              }`}
            >
              {/* Header */}
              <div className="flex items-start justify-between gap-2 mb-2 pb-2 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <Badge
                    label={status}
                    variant={isObserved ? 'blue' : isUncertainty ? 'amber' : 'purple'}
                    size="sm"
                  />
                  <span className="font-mono text-xs font-bold text-slate-900 capitalize">
                    {ev.evidence_type?.replace(/_/g, ' ') || 'Graph Signal'}
                  </span>
                </div>
                <div className="flex items-center gap-1 text-[11px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  <ShieldCheck className="w-3 h-3 text-emerald-600" />
                  <span>Verified Provenance</span>
                </div>
              </div>

              {/* Description */}
              <p className="text-xs text-slate-700 leading-relaxed mb-3">{ev.description}</p>

              {/* Provenance Metadata Grid */}
              <div className="bg-slate-50 p-2.5 rounded border border-slate-200 grid grid-cols-2 gap-2 text-[11px]">
                <div className="flex items-center gap-1.5 text-slate-500">
                  <Database className="w-3 h-3 text-sky-600" />
                  <span>Source:</span>
                  <span className="font-mono font-medium text-slate-800">{ev.source || 'TigerGraph MCP'}</span>
                </div>

                <div className="flex items-center gap-1.5 text-slate-500">
                  <Wrench className="w-3 h-3 text-purple-600" />
                  <span>Tool:</span>
                  <span className="font-mono font-medium text-slate-800">{ev.tool || 'get_transaction_context'}</span>
                </div>

                <div className="flex items-center gap-1.5 text-slate-500">
                  <Layers className="w-3 h-3 text-amber-600" />
                  <span>Step:</span>
                  <span className="font-mono font-medium text-slate-800">#{ev.investigation_step ?? idx + 1}</span>
                </div>

                <div className="flex items-center gap-1.5 text-slate-500">
                  <span>Confidence:</span>
                  <span className="font-mono font-medium text-slate-800">
                    {ev.confidence !== undefined ? `${(ev.confidence * 100).toFixed(0)}%` : '100%'}
                  </span>
                </div>
              </div>

              {/* Entity IDs */}
              {ev.entity_ids && ev.entity_ids.length > 0 && (
                <div className="mt-2.5 flex items-center gap-1.5 flex-wrap">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Entities:</span>
                  {ev.entity_ids.map((ent, i) => (
                    <span
                      key={i}
                      className="text-[10px] font-mono px-1.5 py-0.5 bg-slate-100 text-slate-700 rounded border border-slate-200"
                    >
                      {ent}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
