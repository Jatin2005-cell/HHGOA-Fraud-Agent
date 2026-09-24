import React, { useState } from 'react';
import { Play, RotateCcw, Sparkles } from 'lucide-react';
import type { CreateInvestigationPayload } from '../../api/investigations';

interface InvestigationFormProps {
  onSubmit: (payload: CreateInvestigationPayload) => void;
  isLoading?: boolean;
}

const BENCHMARK_TEMPLATES: Record<string, CreateInvestigationPayload> = {
  'HHG-003': {
    case_id: 'HHG-003',
    trigger_type: 'customer_report',
    trigger_text: 'Customer reports unauthorized transaction of $49.00 on their card',
    flagged_txn_id: '3448408',
    customer_id: 'C10042',
    card_id: 'C10042-K1',
    risk_score: 0.1,
  },
  'HHG-004': {
    case_id: 'HHG-004',
    trigger_type: 'customer_report',
    trigger_text: 'Customer disputes $128.33 transaction after receiving unexpected SMS code',
    flagged_txn_id: '3020297',
    customer_id: 'C10142',
    card_id: 'C10142-K1',
    risk_score: 0.1,
  },
  'HHG-006': {
    case_id: 'HHG-006',
    trigger_type: 'customer_report',
    trigger_text: 'Customer reports unauthorized luxury store purchases totaling $482.12',
    flagged_txn_id: '3330661',
    customer_id: 'C10214',
    card_id: 'C10214-K1',
    risk_score: 0.1,
  },
  'HHG-001': {
    case_id: 'HHG-001',
    trigger_type: 'risk_score',
    trigger_text: 'Real-time ML risk model flagged transaction 3514030 with elevated risk score',
    flagged_txn_id: '3514030',
    customer_id: 'C12382',
    card_id: 'C12382-K1',
    risk_score: 0.75,
  },
};

export const InvestigationForm: React.FC<InvestigationFormProps> = ({ onSubmit, isLoading = false }) => {
  const [formData, setFormData] = useState<CreateInvestigationPayload>({
    case_id: `HHG-${Math.floor(100 + Math.random() * 900)}`,
    trigger_type: 'risk_score',
    trigger_text: 'Real-time high risk transaction score detected by ML pipeline',
    flagged_txn_id: '3514030',
    customer_id: 'C12382',
    card_id: 'C12382-K1',
    risk_score: 0.85,
  });

  const [validationError, setValidationError] = useState<string | null>(null);

  const handleTemplateSelect = (caseKey: string) => {
    if (BENCHMARK_TEMPLATES[caseKey]) {
      setFormData({ ...BENCHMARK_TEMPLATES[caseKey] });
      setValidationError(null);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.case_id.trim()) {
      setValidationError('Case ID is required.');
      return;
    }
    if (!formData.flagged_txn_id.trim()) {
      setValidationError('Transaction ID is required.');
      return;
    }
    if (!formData.customer_id.trim()) {
      setValidationError('Customer ID is required.');
      return;
    }
    if (!formData.card_id.trim()) {
      setValidationError('Card ID is required.');
      return;
    }
    setValidationError(null);
    onSubmit(formData);
  };

  const handleClear = () => {
    setFormData({
      case_id: `HHG-${Math.floor(100 + Math.random() * 900)}`,
      trigger_type: 'risk_score',
      trigger_text: '',
      flagged_txn_id: '',
      customer_id: '',
      card_id: '',
      risk_score: 0.5,
    });
    setValidationError(null);
  };

  return (
    <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm text-left">
      {/* Quick Benchmark Preset Loader */}
      <div className="mb-6 pb-4 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Initiate Fraud Investigation</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Submit a suspicious alert trigger for autonomous multi-hop TigerGraph investigation.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-slate-500 flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            Quick Benchmark Preset:
          </span>
          <select
            onChange={(e) => handleTemplateSelect(e.target.value)}
            defaultValue=""
            className="text-xs h-8 px-2.5 bg-slate-50 border border-slate-300 rounded font-mono text-slate-700 focus:outline-none focus:ring-1 focus:ring-sky-500"
          >
            <option value="" disabled>
              Select Exam Case...
            </option>
            <option value="HHG-003">HHG-003 (Customer Report - Card Theft)</option>
            <option value="HHG-004">HHG-004 (Customer Report - Phishing SAR)</option>
            <option value="HHG-006">HHG-006 (Customer Report - Luxury Fraud SAR)</option>
            <option value="HHG-001">HHG-001 (Risk Score - Legitimate False Positive)</option>
          </select>
        </div>
      </div>

      {validationError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-800 text-xs rounded">
          {validationError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Case ID */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Case ID <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.case_id}
              onChange={(e) => setFormData({ ...formData, case_id: e.target.value })}
              className="w-full h-9 px-3 bg-slate-50 border border-slate-300 rounded text-xs font-mono text-slate-900 focus:outline-none focus:ring-1 focus:ring-sky-500"
              placeholder="e.g. HHG-003"
            />
          </div>

          {/* Trigger Type */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Trigger Type <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.trigger_type}
              onChange={(e) => setFormData({ ...formData, trigger_type: e.target.value })}
              className="w-full h-9 px-2.5 bg-slate-50 border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-sky-500"
            >
              <option value="risk_score">risk_score (ML Model Score)</option>
              <option value="customer_report">customer_report (Customer Inbound Call)</option>
              <option value="analyst_request">analyst_request (Internal Escalation)</option>
            </select>
          </div>

          {/* Risk Score */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Dataset Risk Score (0.00 - 1.00)
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={formData.risk_score ?? ''}
              onChange={(e) =>
                setFormData({ ...formData, risk_score: parseFloat(e.target.value) || 0 })
              }
              className="w-full h-9 px-3 bg-slate-50 border border-slate-300 rounded text-xs font-mono text-slate-900 focus:outline-none focus:ring-1 focus:ring-sky-500"
            />
          </div>
        </div>

        {/* Entities Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Flagged Transaction ID <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.flagged_txn_id}
              onChange={(e) => setFormData({ ...formData, flagged_txn_id: e.target.value })}
              className="w-full h-9 px-3 bg-slate-50 border border-slate-300 rounded text-xs font-mono text-slate-900 focus:outline-none focus:ring-1 focus:ring-sky-500"
              placeholder="e.g. 3448408"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Customer ID <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.customer_id}
              onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
              className="w-full h-9 px-3 bg-slate-50 border border-slate-300 rounded text-xs font-mono text-slate-900 focus:outline-none focus:ring-1 focus:ring-sky-500"
              placeholder="e.g. C10042"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Card ID <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.card_id}
              onChange={(e) => setFormData({ ...formData, card_id: e.target.value })}
              className="w-full h-9 px-3 bg-slate-50 border border-slate-300 rounded text-xs font-mono text-slate-900 focus:outline-none focus:ring-1 focus:ring-sky-500"
              placeholder="e.g. C10042-K1"
            />
          </div>
        </div>

        {/* Trigger Text */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Trigger Alert Description
          </label>
          <textarea
            rows={2}
            value={formData.trigger_text}
            onChange={(e) => setFormData({ ...formData, trigger_text: e.target.value })}
            className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-sky-500"
            placeholder="Describe the inbound alert signal..."
          />
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={handleClear}
            disabled={isLoading}
            className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded transition-colors inline-flex items-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Clear
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="px-5 py-2 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 disabled:bg-slate-400 rounded transition-colors inline-flex items-center gap-1.5 shadow-sm"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            {isLoading ? 'Agent Investigating...' : 'START INVESTIGATION'}
          </button>
        </div>
      </form>
    </div>
  );
};
