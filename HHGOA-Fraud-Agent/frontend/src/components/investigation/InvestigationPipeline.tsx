import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, CircleDot, Clock } from 'lucide-react';

export const PIPELINE_STAGES = [
  { id: 'TRIGGER', label: 'Trigger Ingestion' },
  { id: 'INITIALIZE', label: 'Case Setup' },
  { id: 'COLLECT_EVIDENCE', label: 'Collect Evidence' },
  { id: 'GRAPH_ANALYSIS', label: 'TigerGraph GSQL' },
  { id: 'CASE_MEMORY', label: 'Historical GraphRAG' },
  { id: 'RISK_ASSESSMENT', label: 'Risk Scoring' },
  { id: 'PATTERN_ANALYSIS', label: 'Typology Analysis' },
  { id: 'UNCERTAINTY', label: 'Epistemic Check' },
  { id: 'POLICY', label: 'Bank Policy Engine' },
  { id: 'ACTION', label: 'Action & Routing' },
  { id: 'CASE_WRITEBACK', label: 'TigerGraph Writeback' },
  { id: 'COMPLETED', label: 'Investigation Complete' },
];

interface InvestigationPipelineProps {
  currentStageIndex: number;
  isComplete?: boolean;
}

export const InvestigationPipeline: React.FC<InvestigationPipelineProps> = ({
  currentStageIndex,
  isComplete = false,
}) => {
  return (
    <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
          Autonomous Investigation Pipeline (TigerGraph + Agentic GraphRAG)
        </h4>
        <span className="text-xs font-mono text-sky-700 bg-sky-50 px-2 py-0.5 rounded border border-sky-200">
          {isComplete
            ? 'Completed (12/12 Stages)'
            : `Executing: Stage ${Math.min(currentStageIndex + 1, 12)} / 12`}
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
        {PIPELINE_STAGES.map((stage, idx) => {
          const isDone = isComplete || idx < currentStageIndex;
          const isCurrent = !isComplete && idx === currentStageIndex;

          return (
            <motion.div
              key={stage.id}
              initial={{ opacity: 0.8 }}
              animate={{ opacity: 1 }}
              className={`p-2.5 rounded border text-left flex items-start gap-2 transition-all ${
                isDone
                  ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900'
                  : isCurrent
                  ? 'bg-sky-50 border-sky-300 text-sky-950 ring-2 ring-sky-500/20'
                  : 'bg-slate-50 border-slate-200 text-slate-400'
              }`}
            >
              <div className="mt-0.5 shrink-0">
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                ) : isCurrent ? (
                  <CircleDot className="w-4 h-4 text-sky-600 animate-pulse" />
                ) : (
                  <Clock className="w-4 h-4 text-slate-300" />
                )}
              </div>
              <div className="min-w-0">
                <div className="text-[10px] font-mono uppercase text-slate-500 leading-tight">
                  Step {idx + 1}
                </div>
                <div
                  className={`text-xs font-medium truncate ${
                    isDone ? 'text-emerald-950 font-semibold' : isCurrent ? 'text-sky-950 font-semibold' : 'text-slate-500'
                  }`}
                >
                  {stage.label}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
