import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  PieChart,
  Pie,
  Legend,
} from 'recharts';

interface CaseStatusChartProps {
  data: Array<{ name: string; count: number }>;
}

export const CaseStatusChart: React.FC<CaseStatusChartProps> = ({ data }) => {
  const STATUS_COLORS: Record<string, string> = {
    RESOLVED: '#16a34a',
    CLOSED: '#059669',
    APPROVAL_PENDING: '#d97706',
    INVESTIGATING: '#0284c7',
    REVIEW: '#f59e0b',
    FAILED: '#dc2626',
    CANCELLED: '#64748b',
    NEW: '#94a3b8',
  };

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
          <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} interval={0} angle={-25} textAnchor="end" />
          <YAxis tick={{ fontSize: 11, fill: '#64748b' }} allowDecimals={false} />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderRadius: '6px', color: '#fff', fontSize: '12px' }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.name] || '#0284c7'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

interface PatternBarChartProps {
  data: Array<{ name: string; count: number }>;
}

export const PatternBarChart: React.FC<PatternBarChartProps> = ({ data }) => {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart layout="vertical" data={data} margin={{ top: 10, right: 20, left: 40, bottom: 10 }}>
          <XAxis type="number" tick={{ fontSize: 11, fill: '#64748b' }} allowDecimals={false} />
          <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: '#334155' }} width={120} />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderRadius: '6px', color: '#fff', fontSize: '12px' }}
          />
          <Bar dataKey="count" fill="#7c3aed" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

interface RiskDistributionChartProps {
  data: Array<{ band: string; count: number }>;
}

export const RiskDistributionChart: React.FC<RiskDistributionChartProps> = ({ data }) => {
  const BAND_COLORS: Record<string, string> = {
    'High (>=0.7)': '#dc2626',
    'Medium (0.4-0.69)': '#d97706',
    'Low (<0.4)': '#16a34a',
  };

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
          <XAxis dataKey="band" tick={{ fontSize: 10, fill: '#64748b' }} />
          <YAxis tick={{ fontSize: 11, fill: '#64748b' }} allowDecimals={false} />
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderRadius: '6px', color: '#fff', fontSize: '12px' }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-risk-${index}`} fill={BAND_COLORS[entry.band] || '#0284c7'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

interface ApprovalPieChartProps {
  data: Array<{ route: string; count: number }>;
}

export const ApprovalPieChart: React.FC<ApprovalPieChartProps> = ({ data }) => {
  const COLORS = ['#0284c7', '#d97706', '#dc2626'];

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={75}
            paddingAngle={3}
            dataKey="count"
            nameKey="route"
          >
            {data.map((_, index) => (
              <Cell key={`cell-appr-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderRadius: '6px', color: '#fff', fontSize: '12px' }}
          />
          <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
