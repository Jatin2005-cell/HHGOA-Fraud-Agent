import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  RefreshCw,
  Database,
  ShieldAlert,
  Network,
  FileText,
  Clock,
  Zap,
  CheckSquare,
  FileSpreadsheet,
  BrainCircuit,
} from 'lucide-react';
import { fetchCaseById } from '../api/cases';
import type { DynamicCase } from '../types/case';
import { OverviewTab } from '../components/case_details/OverviewTab';
import { GraphTab } from '../components/case_details/GraphTab';
import { EvidenceTab } from '../components/case_details/EvidenceTab';
import { TimelineTab } from '../components/case_details/TimelineTab';
import { ActionsTab } from '../components/case_details/ActionsTab';
import { ApprovalTab } from '../components/case_details/ApprovalTab';
import { SarTab } from '../components/case_details/SarTab';
import { AiExplanationTab } from '../components/case_details/AiExplanationTab';
import { Skeleton } from '../components/common/Skeleton';
import { ErrorState } from '../components/common/ErrorState';
import { getVerdictVisual, getLifecycleStatusVisual, getRiskTierVisual } from '../utils/risk';

type TabKey =
  | 'overview'
  | 'graph'
  | 'evidence'
  | 'timeline'
  | 'actions'
  | 'approval'
  | 'sar'
  | 'explanation';

export const CaseDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState<DynamicCase | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('overview');

  const loadCase = async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchCaseById(id);
      setCaseData(data);
    } catch (err: any) {
      setError(err.message || `Failed to retrieve case details for ${id}.`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCase();
  }, [id]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-16 rounded-lg" />
        <Skeleton className="h-12 rounded-lg" />
        <Skeleton className="h-96 rounded-lg" />
      </div>
    );
  }

  if (error || !caseData) {
    return (
      <ErrorState
        message={error || `Case ${id} not found.`}
        onRetry={loadCase}
      />
    );
  }

  const verdictVis = getVerdictVisual(caseData.verdict);
  const statusVis = getLifecycleStatusVisual(caseData.status);
  const riskVis = getRiskTierVisual(caseData.risk_score ?? caseData.fraud_probability);

  const tabs: { key: TabKey; label: string; icon: React.FC<{ className?: string }> }[] = [
    { key: 'overview', label: 'Overview', icon: ShieldAlert },
    { key: 'graph', label: 'Evidence Graph', icon: Network },
    { key: 'evidence', label: 'Evidence Items', icon: FileText },
    { key: 'timeline', label: 'FSM Timeline', icon: Clock },
    { key: 'actions', label: 'Actions', icon: Zap },
    { key: 'approval', label: 'Governance', icon: CheckSquare },
    { key: 'sar', label: 'SAR Filing', icon: FileSpreadsheet },
    { key: 'explanation', label: 'AI Explanation', icon: BrainCircuit },
  ];

  return (
    <div className="space-y-6 text-left">
      {/* Top Breadcrumb & Action Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/cases')}
            className="p-1.5 text-slate-500 hover:text-slate-900 bg-white border border-slate-200 rounded-md hover:bg-slate-50 transition-colors shadow-sm"
            title="Back to Case List"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold font-mono tracking-tight text-slate-900">
                {caseData.case_id}
              </h1>
              <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${verdictVis.bgClass} ${verdictVis.textClass} ${verdictVis.borderClass}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${verdictVis.dotClass}`} />
                {verdictVis.label}
              </span>
              <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${statusVis.bgClass} ${statusVis.textClass} ${statusVis.borderClass}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${statusVis.dotClass}`} />
                {statusVis.label}
              </span>
              <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${riskVis.bgClass} ${riskVis.textClass} ${riskVis.borderClass}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${riskVis.dotClass}`} />
                {riskVis.label}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Trigger: <span className="font-semibold text-slate-700">{caseData.trigger_type}</span> | Card: <span className="font-mono text-slate-700">{caseData.card_id}</span> | Customer: <span className="font-mono text-slate-700">{caseData.customer_id}</span>
            </p>
          </div>
        </div>

        {/* Runtime Provenance Badge */}
        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-lg bg-amber-50 border border-amber-300/80 text-amber-900 text-xs flex items-center gap-2 shadow-sm">
            <Database className="w-3.5 h-3.5 text-amber-700 shrink-0" />
            <span>
              Provenance: <strong>{caseData.provenance?.evidence_provenance || 'LOCAL_STAGED_DATASET'}</strong>
            </span>
            <span className="font-mono text-[10px] text-amber-800 border-l border-amber-300 pl-2">
              {caseData.provenance?.execution_mode || 'OFFLINE_STAGED_SIMULATION'}
            </span>
          </div>

          <button
            onClick={loadCase}
            className="p-2 text-slate-500 hover:text-slate-800 bg-white border border-slate-200 rounded-md hover:bg-slate-50 shadow-sm transition-colors"
            title="Refresh case details"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex items-center gap-1 border-b border-slate-200 overflow-x-auto pb-px">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-t-md border-b-2 transition-all whitespace-nowrap ${
                isActive
                  ? 'border-sky-600 text-sky-700 bg-sky-50/50'
                  : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Active Tab Panel */}
      <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm min-h-[460px]">
        {activeTab === 'overview' && <OverviewTab caseData={caseData} />}
        {activeTab === 'graph' && <GraphTab caseId={caseData.case_id} />}
        {activeTab === 'evidence' && (
          <EvidenceTab evidenceList={caseData.evidence || []} />
        )}
        {activeTab === 'timeline' && (
          <TimelineTab timeline={caseData.timeline || []} />
        )}
        {activeTab === 'actions' && (
          <ActionsTab
            initialActions={caseData.initial_actions}
            finalActions={caseData.final_actions}
            whatChanged={caseData.what_changed}
            approvalRoute={caseData.approval_route || 'auto'}
            approvalStatus={caseData.approval_status || 'NOT_REQUIRED'}
          />
        )}
        {activeTab === 'approval' && (
          <ApprovalTab caseData={caseData} onRefresh={loadCase} />
        )}
        {activeTab === 'sar' && (
          <SarTab
            caseId={caseData.case_id}
            sarRequired={caseData.sar_required || false}
          />
        )}
        {activeTab === 'explanation' && (
          <AiExplanationTab caseData={caseData} />
        )}
      </div>
    </div>
  );
};
