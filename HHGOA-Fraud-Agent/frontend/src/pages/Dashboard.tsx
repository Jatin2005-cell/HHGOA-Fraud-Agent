import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Briefcase,
  AlertTriangle,
  Clock,
  FileSpreadsheet,
  ShieldAlert,
  Search,
  TrendingUp,
  Activity,
  Terminal,
} from 'lucide-react';
import { fetchDashboardSummary, fetchDashboardDistributions } from '../api/cases';
import { KpiCard } from '../components/dashboard/KpiCard';
import {
  CaseStatusChart,
  PatternBarChart,
  RiskDistributionChart,
  ApprovalPieChart,
} from '../components/dashboard/CaseCharts';
import { Skeleton } from '../components/common/Skeleton';
import { ErrorState } from '../components/common/ErrorState';
import { formatCurrency } from '../utils/formatters';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<any>(null);
  const [dist, setDist] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [sumData, distData] = await Promise.all([
        fetchDashboardSummary(),
        fetchDashboardDistributions(),
      ]);
      setSummary(sumData);
      setDist(distData);
    } catch (err: any) {
      setError(err.message || 'Failed to load executive dashboard statistics.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (error) {
    return <ErrorState message={error} onRetry={loadData} />;
  }

  return (
    <div className="space-y-6 text-left min-h-screen bg-[#0B0F17] text-slate-200 p-6 font-sans">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-2 bg-sky-500/10 border border-sky-500/20 rounded-lg text-sky-400">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                FRAUD OPERATIONS COMMAND DASHBOARD
              </h1>
              <p className="text-xs text-slate-400 mt-0.5 font-mono">
                Real-time GSQL Graph Engine & Autonomous Agent Telemetry Stream
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={() => navigate('/investigate')}
          className="px-4 py-2 text-xs font-mono font-semibold text-white bg-sky-600 hover:bg-sky-500 rounded-lg transition-all shadow-lg shadow-sky-600/20 inline-flex items-center gap-2 border border-sky-400/30"
        >
          <Search className="w-4 h-4" />
          <span>LAUNCH INVESTIGATION</span>
        </button>
      </div>

      {/* KPI Cards Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl bg-slate-900 border border-slate-800" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard
            label="Total Cases"
            value={summary?.total_cases ?? 0}
            subtitle="Persisted Dynamic Case Store"
            icon={Briefcase}
            variant="blue"
          />
          <KpiCard
            label="Open Investigations"
            value={summary?.open_investigations ?? 0}
            subtitle="Active State Traversal"
            icon={Clock}
            variant="amber"
          />
          <KpiCard
            label="High Risk Alerts"
            value={summary?.high_risk_cases ?? 0}
            subtitle="Risk Score ≥ 0.70 Threshold"
            icon={AlertTriangle}
            variant="red"
          />
          <KpiCard
            label="Pending Governance"
            value={summary?.pending_approvals ?? 0}
            subtitle="L1 Lead / L2 Sign-off Required"
            icon={ShieldAlert}
            variant="amber"
          />
          <KpiCard
            label="SAR Filings Mandated"
            value={summary?.sar_required ?? 0}
            subtitle="FinCEN Form Drafts"
            icon={FileSpreadsheet}
            variant="purple"
          />
          <KpiCard
            label="Confirmed Fraud"
            value={summary?.fraud_investigations ?? 0}
            subtitle="Identified Typology Patterns"
            icon={ShieldAlert}
            variant="red"
          />
          <KpiCard
            label="Uncertain Signals"
            value={summary?.uncertain_cases ?? 0}
            subtitle="Verification Signal Pending"
            icon={Clock}
            variant="amber"
          />
          <KpiCard
            label="Total Exposure Scope"
            value={formatCurrency(summary?.total_exposure_usd ?? 0)}
            subtitle="Cumulative Risk Exposure"
            icon={TrendingUp}
            variant="green"
          />
        </div>
      )}

      {/* Analytics Visualization Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
            <div>
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">Lifecycle Phase Distribution</h3>
              <p className="text-[11px] text-slate-400 font-mono">Finite State Machine phase classification</p>
            </div>
            <Terminal className="w-4 h-4 text-slate-500" />
          </div>
          {isLoading ? <Skeleton className="h-64 rounded bg-slate-800/50" /> : <CaseStatusChart data={dist?.cases_by_status || []} />}
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
            <div>
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">Fraud Pattern Typologies</h3>
              <p className="text-[11px] text-slate-400 font-mono">CNP, Stolen Card, Account Takeover breakdown</p>
            </div>
            <Terminal className="w-4 h-4 text-slate-500" />
          </div>
          {isLoading ? <Skeleton className="h-64 rounded bg-slate-800/50" /> : <PatternBarChart data={dist?.cases_by_pattern || []} />}
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
            <div>
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">Risk Severity Bands</h3>
              <p className="text-[11px] text-slate-400 font-mono">High (≥0.70), Medium, and Low risk stratification</p>
            </div>
            <Terminal className="w-4 h-4 text-slate-500" />
          </div>
          {isLoading ? <Skeleton className="h-64 rounded bg-slate-800/50" /> : <RiskDistributionChart data={dist?.risk_distribution || []} />}
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
            <div>
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">Approval Hierarchy Breakdown</h3>
              <p className="text-[11px] text-slate-400 font-mono">Auto execution vs Human Lead Escalation</p>
            </div>
            <Terminal className="w-4 h-4 text-slate-500" />
          </div>
          {isLoading ? <Skeleton className="h-64 rounded bg-slate-800/50" /> : <ApprovalPieChart data={dist?.approval_distribution || []} />}
        </div>
      </div>
    </div>
  );
};