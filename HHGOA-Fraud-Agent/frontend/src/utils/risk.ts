export interface StatusVisual {
  label: string;
  bgClass: string;
  textClass: string;
  borderClass: string;
  dotClass: string;
}

export function getVerdictVisual(verdict: string | null | undefined): StatusVisual {
  const v = (verdict || '').toLowerCase();
  if (v.includes('fraud')) {
    return {
      label: 'CONFIRMED FRAUD',
      bgClass: 'bg-red-50',
      textClass: 'text-red-700',
      borderClass: 'border-red-200',
      dotClass: 'bg-red-600',
    };
  }
  if (v.includes('legit')) {
    return {
      label: 'LEGITIMATE',
      bgClass: 'bg-emerald-50',
      textClass: 'text-emerald-700',
      borderClass: 'border-emerald-200',
      dotClass: 'bg-emerald-600',
    };
  }
  return {
    label: 'UNCERTAIN / REVIEW',
    bgClass: 'bg-amber-50',
    textClass: 'text-amber-700',
    borderClass: 'border-amber-200',
    dotClass: 'bg-amber-600',
  };
}

export function getLifecycleStatusVisual(status: string | null | undefined): StatusVisual {
  const s = (status || '').toUpperCase();
  switch (s) {
    case 'RESOLVED':
    case 'CLOSED':
      return {
        label: s,
        bgClass: 'bg-emerald-50',
        textClass: 'text-emerald-700',
        borderClass: 'border-emerald-200',
        dotClass: 'bg-emerald-600',
      };
    case 'APPROVAL_PENDING':
    case 'REVIEW':
    case 'EVIDENCE_PENDING':
      return {
        label: s.replace('_', ' '),
        bgClass: 'bg-amber-50',
        textClass: 'text-amber-700',
        borderClass: 'border-amber-200',
        dotClass: 'bg-amber-600',
      };
    case 'INVESTIGATING':
    case 'ACTION_REQUIRED':
      return {
        label: s.replace('_', ' '),
        bgClass: 'bg-sky-50',
        textClass: 'text-sky-700',
        borderClass: 'border-sky-200',
        dotClass: 'bg-sky-600',
      };
    case 'FAILED':
    case 'CANCELLED':
      return {
        label: s,
        bgClass: 'bg-rose-50',
        textClass: 'text-rose-700',
        borderClass: 'border-rose-200',
        dotClass: 'bg-rose-600',
      };
    default:
      return {
        label: s || 'NEW',
        bgClass: 'bg-slate-100',
        textClass: 'text-slate-700',
        borderClass: 'border-slate-200',
        dotClass: 'bg-slate-500',
      };
  }
}

export function getRiskTierVisual(riskScore: number | null | undefined): StatusVisual {
  const score = riskScore ?? 0;
  if (score >= 0.7) {
    return {
      label: `HIGH RISK (${score.toFixed(2)})`,
      bgClass: 'bg-red-50',
      textClass: 'text-red-700',
      borderClass: 'border-red-200',
      dotClass: 'bg-red-600',
    };
  }
  if (score >= 0.4) {
    return {
      label: `MEDIUM RISK (${score.toFixed(2)})`,
      bgClass: 'bg-amber-50',
      textClass: 'text-amber-700',
      borderClass: 'border-amber-200',
      dotClass: 'bg-amber-600',
    };
  }
  return {
    label: `LOW RISK (${score.toFixed(2)})`,
    bgClass: 'bg-emerald-50',
    textClass: 'text-emerald-700',
    borderClass: 'border-emerald-200',
    dotClass: 'bg-emerald-600',
  };
}
