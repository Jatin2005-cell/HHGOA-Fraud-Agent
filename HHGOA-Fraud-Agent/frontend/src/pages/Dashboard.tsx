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
  ShieldCheck,
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
    <div className="space-y-8 text-left min-h-screen bg-[#0B0F17] text-slate-200 p-6 font-sans">
      {/* Executive Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/60 pb-6 pt-2">
        <div className="flex items-center gap-4">
          {/* Glowing Icon Container */}
          <div className="p-3 bg-gradient-to-br from-sky-500/20 to-blue-600/10 border border-sky-500/30 rounded-2xl text-sky-400 shadow-lg shadow-sky-500/10">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>

          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                Executive Fraud Intelligence
              </h1>
              {/* Live Status Badge */}
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                Live Agent Active
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-1 font-normal">
              Real-time threat monitoring, graph analytics, and autonomous risk detection
            </p>
          </div>
        </div>

        {/* Primary Action Button */}
        <button
          onClick={() => navigate('/investigate')}
          className="px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 rounded-xl transition-all duration-200 shadow-lg shadow-sky-500/25 active:scale-95 inline-flex items-center gap-2 border border-sky-300/30 cursor-pointer"
        >
          <Search className="w-4 h-4" />
          <span>Launch New Investigation</span>
        </button>
      </div>

      {/* KPI Cards Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-2xl bg-slate-900 border border-slate-800/80" />
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
            icon={ShieldCheck}
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
        <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 shadow-xl backdrop-blur-md hover:border-slate-700/80 transition-all duration-300">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-5">
            <div>
              <h3 className="text-sm font-semibold text-slate-100 tracking-wide">Lifecycle Phase Distribution</h3>
              <p className="text-xs text-slate-400 mt-0.5">Finite State Machine phase classification</p>
            </div>
            <Terminal className="w-4 h-4 text-slate-500" />
          </div>
          {isLoading ? <Skeleton className="h-64 rounded-xl bg-slate-800/50" /> : <CaseStatusChart data={dist?.cases_by_status || []} />}
        </div>

        <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 shadow-xl backdrop-blur-md hover:border-slate-700/80 transition-all duration-300">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-5">
            <div>
              <h3 className="text-sm font-semibold text-slate-100 tracking-wide">Fraud Pattern Typologies</h3>
              <p className="text-xs text-slate-400 mt-0.5">CNP, Stolen Card, Account Takeover breakdown</p>
            </div>
            <Terminal className="w-4 h-4 text-slate-500" />
          </div>
          {isLoading ? <Skeleton className="h-64 rounded-xl bg-slate-800/50" /> : <PatternBarChart data={dist?.cases_by_pattern || []} />}
        </div>

        <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 shadow-xl backdrop-blur-md hover:border-slate-700/80 transition-all duration-300">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-5">
            <div>
              <h3 className="text-sm font-semibold text-slate-100 tracking-wide">Risk Severity Bands</h3>
              <p className="text-xs text-slate-400 mt-0.5">High (≥0.70), Medium, and Low risk stratification</p>
            </div>
            <Terminal className="w-4 h-4 text-slate-500" />
          </div>
          {isLoading ? <Skeleton className="h-64 rounded-xl bg-slate-800/50" /> : <RiskDistributionChart data={dist?.risk_distribution || []} />}
        </div>

        <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 shadow-xl backdrop-blur-md hover:border-slate-700/80 transition-all duration-300">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-5">
            <div>
              <h3 className="text-sm font-semibold text-slate-100 tracking-wide">Approval Hierarchy Breakdown</h3>
              <p className="text-xs text-slate-400 mt-0.5">Auto execution vs Human Lead Escalation</p>
            </div>
            <Terminal className="w-4 h-4 text-slate-500" />
          </div>
          {isLoading ? <Skeleton className="h-64 rounded-xl bg-slate-800/50" /> : <ApprovalPieChart data={dist?.approval_distribution || []} />}
        </div>
      </div>
    </div>
  );
};