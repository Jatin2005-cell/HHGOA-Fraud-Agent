import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface KpiCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'blue' | 'green' | 'red' | 'amber' | 'purple' | 'slate';
  badge?: string;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  label,
  value,
  subtitle,
  icon: Icon,
  variant = 'blue',
  badge,
}) => {
  const borderStyles = {
    blue: 'border-l-4 border-l-sky-600',
    green: 'border-l-4 border-l-emerald-600',
    red: 'border-l-4 border-l-red-600',
    amber: 'border-l-4 border-l-amber-600',
    purple: 'border-l-4 border-l-purple-600',
    slate: 'border-l-4 border-l-slate-600',
  };

  const iconBgStyles = {
    blue: 'bg-sky-50 text-sky-700',
    green: 'bg-emerald-50 text-emerald-700',
    red: 'bg-red-50 text-red-700',
    amber: 'bg-amber-50 text-amber-700',
    purple: 'bg-purple-50 text-purple-700',
    slate: 'bg-slate-100 text-slate-700',
  };

  return (
    <div
      className={`bg-white rounded-lg border border-slate-200 p-4 shadow-sm flex items-start justify-between ${borderStyles[variant]}`}
    >
      <div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{label}</span>
          {badge && (
            <span className="text-[10px] px-1.5 py-0.2 bg-slate-100 text-slate-600 rounded font-medium">
              {badge}
            </span>
          )}
        </div>
        <div className="text-2xl font-bold text-slate-900 mt-1 tracking-tight">{value}</div>
        {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
      </div>
      <div className={`p-2.5 rounded-lg ${iconBgStyles[variant]}`}>
        <Icon className="w-5 h-5" />
      </div>
    </div>
  );
};
