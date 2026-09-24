import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';
import type { CaseFilterParams } from '../../api/cases';

interface CaseFilterBarProps {
  filters: CaseFilterParams;
  onChange: (newFilters: CaseFilterParams) => void;
  onReset: () => void;
}

export const CaseFilterBar: React.FC<CaseFilterBarProps> = ({ filters, onChange, onReset }) => {
  return (
    <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm mb-4">
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 mr-2">
          <Filter className="w-3.5 h-3.5 text-sky-600" />
          <span>Filters:</span>
        </div>

        {/* Status Filter */}
        <select
          value={filters.status || ''}
          onChange={(e) => onChange({ ...filters, status: e.target.value || undefined, page: 1 })}
          className="text-xs h-8 px-2.5 bg-slate-50 border border-slate-300 rounded text-slate-700 focus:outline-none focus:ring-1 focus:ring-sky-500"
        >
          <option value="">All Statuses</option>
          <option value="NEW">NEW</option>
          <option value="INVESTIGATING">INVESTIGATING</option>
          <option value="APPROVAL_PENDING">APPROVAL_PENDING</option>
          <option value="REVIEW">REVIEW</option>
          <option value="RESOLVED">RESOLVED</option>
          <option value="CLOSED">CLOSED</option>
          <option value="ESCALATED">ESCALATED</option>
        </select>

        {/* Risk Level Filter */}
        <select
          value={filters.risk_level || ''}
          onChange={(e) => onChange({ ...filters, risk_level: e.target.value || undefined, page: 1 })}
          className="text-xs h-8 px-2.5 bg-slate-50 border border-slate-300 rounded text-slate-700 focus:outline-none focus:ring-1 focus:ring-sky-500"
        >
          <option value="">All Risk Levels</option>
          <option value="HIGH">High Risk (&ge; 0.70)</option>
          <option value="MEDIUM">Medium Risk (0.40 - 0.69)</option>
          <option value="LOW">Low Risk (&lt; 0.40)</option>
        </select>

        {/* Approval Route */}
        <select
          value={filters.approval_status || ''}
          onChange={(e) => onChange({ ...filters, approval_status: e.target.value || undefined, page: 1 })}
          className="text-xs h-8 px-2.5 bg-slate-50 border border-slate-300 rounded text-slate-700 focus:outline-none focus:ring-1 focus:ring-sky-500"
        >
          <option value="">All Approval States</option>
          <option value="PENDING">PENDING</option>
          <option value="APPROVED">APPROVED</option>
          <option value="REJECTED">REJECTED</option>
        </select>

        {/* SAR Status */}
        <select
          value={filters.sar_status || ''}
          onChange={(e) => onChange({ ...filters, sar_status: e.target.value || undefined, page: 1 })}
          className="text-xs h-8 px-2.5 bg-slate-50 border border-slate-300 rounded text-slate-700 focus:outline-none focus:ring-1 focus:ring-sky-500"
        >
          <option value="">All SAR States</option>
          <option value="GENERATED">GENERATED / MANDATED</option>
          <option value="NOT_REQUIRED">NOT REQUIRED</option>
        </select>

        {/* Reset Button */}
        <button
          onClick={onReset}
          className="ml-auto inline-flex items-center gap-1 text-xs font-medium text-slate-500 hover:text-slate-800 px-2.5 py-1.5 rounded hover:bg-slate-100 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Filters</span>
        </button>
      </div>
    </div>
  );
};
