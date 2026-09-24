import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Database, CheckCircle2, AlertTriangle, Cpu, ShieldCheck } from 'lucide-react';
import { InvestigationForm } from '../components/investigation/InvestigationForm';
import { InvestigationPipeline } from '../components/investigation/InvestigationPipeline';
import { createInvestigation, runInvestigation } from '../api/investigations';
import type { CreateInvestigationPayload } from '../api/investigations';

export const Investigate: React.FC = () => {
  const navigate = useNavigate();
  const [isRunning, setIsRunning] = useState(false);
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [investigationResult, setInvestigationResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleLaunch = async (payload: CreateInvestigationPayload) => {
    setIsRunning(true);
    setError(null);
    setCurrentStageIndex(0);
    setIsComplete(false);
    setInvestigationResult(null);

    try {
      setCurrentStageIndex(1);
      await createInvestigation(payload);

      setCurrentStageIndex(5);
      const result = await runInvestigation(payload.case_id);

      setCurrentStageIndex(11);
      setIsComplete(true);
      setInvestigationResult(result);
    } catch (err: any) {
      setError(err.message || 'Investigation execution failed.');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6 text-left min-h-screen bg-[#0B0F17] text-slate-200 p-6 font-sans">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-sky-500/10 border border-sky-500/20 rounded-lg text-sky-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                AUTONOMOUS INVESTIGATION PIPELINE
                <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-sky-950 text-sky-400 font-semibold border border-sky-800">
                  17-STATE FSM AGENT
                </span>
              </h1>
              <p className="text-xs text-slate-400 mt-0.5 font-mono">
                Initiate automated graph query, risk scoring, and SAR drafting sequence
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Form Configuration */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md">
            <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200 border-b border-slate-800 pb-2 mb-4">
              Alert Launch Parameters
            </h2>
            <InvestigationForm onSubmit={handleLaunch} isLoading={isRunning} />
          </div>
        </div>

        {/* Right Column: Live Pipeline Feed */}
        <div className="lg:col-span-7 space-y-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md">
            <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200 border-b border-slate-800 pb-2 mb-4">
              Real-time Execution Telemetry
            </h2>

            <InvestigationPipeline currentStageIndex={currentStageIndex} isComplete={isComplete} />

            {error && (
              <div className="mt-4 p-4 bg-rose-950/40 border border-rose-500/30 rounded-xl text-xs text-rose-300 flex items-start gap-3">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-mono font-bold block uppercase tracking-wider text-rose-400">Execution Error</span>
                  <span className="font-mono">{error}</span>
                </div>
              </div>
            )}

            {investigationResult && (
              <div className="mt-6 pt-6 border-t border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    <span className="font-mono font-bold text-white text-sm">
                      INVESTIGATION COMPLETED: {investigationResult.case_id}
                    </span>
                  </div>
                  <button
                    onClick={() => navigate(`/cases/${investigationResult.case_id}`)}
                    className="px-3.5 py-1.5 text-xs font-mono font-semibold text-white bg-sky-600 hover:bg-sky-500 rounded-lg transition-all shadow-md inline-flex items-center gap-2 border border-sky-400/30"
                  >
                    <span>OPEN WORKSPACE</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* KPI Result Strip */}
                <div className="grid grid-cols-3 gap-3 text-xs font-mono">
                  <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Verdict Signal</span>
                    <span
                      className={`text-sm font-bold uppercase ${
                        investigationResult.verdict === 'fraud'
                          ? 'text-rose-400'
                          : investigationResult.verdict === 'suspicious'
                          ? 'text-amber-400'
                          : 'text-emerald-400'
                      }`}
                    >
                      {investigationResult.verdict}
                    </span>
                  </div>

                  <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Probability Score</span>
                    <span className="text-sm font-bold text-white">
                      {((investigationResult.risk?.fraud_probability || 0) * 100).toFixed(1)}%
                    </span>
                  </div>

                  <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Governance Route</span>
                    <span className="text-sm font-bold text-sky-400">
                      {investigationResult.approval_route || 'Standard'}
                    </span>
                  </div>
                </div>

                {/* Provenance Tag */}
                <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-500/20 text-xs font-mono text-amber-300 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Database className="w-4 h-4 text-amber-400" />
                    <span>
                      Provenance: <strong>{investigationResult.provenance?.evidence_provenance || 'LOCAL_STAGED_DATASET'}</strong>
                    </span>
                  </div>
                  <span className="text-[11px] font-bold text-amber-400">
                    {investigationResult.provenance?.execution_mode || 'OFFLINE_STAGED_SIMULATION'}
                  </span>
                </div>

                {/* Agent Summary Block */}
                <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 leading-relaxed shadow-inner">
                  <div className="text-[10px] uppercase text-slate-500 font-bold mb-1 flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-sky-400" />
                    Agent Reasoning Synthesis
                  </div>
                  {investigationResult.summary}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};