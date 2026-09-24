import React from 'react';
import type { TimelineEvent } from '../../types/case';
import { formatDateTime } from '../../utils/dates';
import { Clock, Cpu, UserCheck, Shield } from 'lucide-react';

interface TimelineTabProps {
  timeline: TimelineEvent[];
}

export const TimelineTab: React.FC<TimelineTabProps> = ({ timeline }) => {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="py-12 text-center text-slate-500 text-xs bg-white rounded-lg border border-slate-200">
        No chronological timeline events recorded.
      </div>
    );
  }

  const getActorIcon = (actor: string) => {
    const a = actor.toLowerCase();
    if (a.includes('agent') || a.includes('orchestrator')) {
      return Cpu;
    }
    if (a.includes('human') || a.includes('manager') || a.includes('lead')) {
      return UserCheck;
    }
    return Shield;
  };

  return (
    <div className="space-y-4 text-left">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
          Investigation Audit & Execution Timeline ({timeline.length} Events)
        </h4>
        <span className="text-[11px] text-slate-500">
          Immutable sequential order with microsecond timestamp provenance.
        </span>
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
        {timeline.map((item, idx) => {
          const Icon = getActorIcon(item.actor);
          return (
            <div key={idx} className="relative group">
              {/* Dot */}
              <div className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-white border-2 border-sky-600 flex items-center justify-center text-sky-600 shadow-xs">
                <span className="w-1.5 h-1.5 rounded-full bg-sky-600" />
              </div>

              {/* Event Card */}
              <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-xs hover:border-slate-300 transition-colors">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-slate-900 uppercase">
                      {item.event_type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 bg-slate-100 text-slate-600 rounded flex items-center gap-1">
                      <Icon className="w-3 h-3 text-sky-600" />
                      {item.actor}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-[11px] text-slate-500 font-mono">
                    <Clock className="w-3 h-3" />
                    <span>{formatDateTime(item.timestamp)}</span>
                  </div>
                </div>

                <p className="text-xs text-slate-700 leading-relaxed">{item.description}</p>

                {(item.tool || item.evidence_ref) && (
                  <div className="mt-2.5 pt-2 border-t border-slate-50 flex items-center gap-3 text-[10px] font-mono text-slate-500">
                    {item.tool && (
                      <span className="bg-purple-50 text-purple-700 px-2 py-0.5 rounded border border-purple-200">
                        Tool: {item.tool}
                      </span>
                    )}
                    {item.evidence_ref && (
                      <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                        Ref: {item.evidence_ref}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
