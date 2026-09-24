import React from 'react';

interface BadgeProps {
  label: string;
  variant?: 'blue' | 'green' | 'red' | 'amber' | 'purple' | 'slate';
  size?: 'sm' | 'md';
  showDot?: boolean;
  pulse?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  label,
  variant = 'blue',
  size = 'md',
  showDot = true,
  pulse = false,
}) => {
  const variantStyles = {
    blue: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
    green: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    red: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    slate: 'bg-slate-800/80 text-slate-300 border-slate-700',
  };

  const dotStyles = {
    blue: 'bg-sky-400',
    green: 'bg-emerald-400',
    red: 'bg-rose-500',
    amber: 'bg-amber-400',
    purple: 'bg-purple-400',
    slate: 'bg-slate-400',
  };

  const sizeStyles = {
    sm: 'text-[10px] px-2 py-0.5',
    md: 'text-[11px] px-2.5 py-0.5',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-mono font-semibold uppercase tracking-wider rounded-full border backdrop-blur-sm ${variantStyles[variant]} ${sizeStyles[size]}`}
    >
      {showDot && (
        <span className="relative flex h-1.5 w-1.5">
          {(pulse || variant === 'red' || variant === 'amber') && (
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${dotStyles[variant]}`} />
          )}
          <span className={`relative inline-flex rounded-full h-1.5 w-1.5 ${dotStyles[variant]}`} />
        </span>
      )}
      <span>{label}</span>
    </span>
  );
};