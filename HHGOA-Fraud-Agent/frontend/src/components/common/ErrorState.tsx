import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message: string;
  errorCode?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Service Unavailable',
  message,
  errorCode,
  onRetry,
}) => {
  return (
    <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
      <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
      <div className="flex-1 text-left">
        <div className="flex items-center gap-2">
          <h4 className="text-sm font-semibold text-red-900">{title}</h4>
          {errorCode && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 bg-red-100 text-red-800 rounded">
              {errorCode}
            </span>
          )}
        </div>
        <p className="text-xs text-red-700 mt-1">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-3 inline-flex items-center gap-1.5 text-xs font-medium text-red-800 bg-red-100 hover:bg-red-200 px-2.5 py-1 rounded transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry Connection
          </button>
        )}
      </div>
    </div>
  );
};
