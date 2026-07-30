import { CheckCircle2, AlertTriangle } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';

const THRESHOLD = 55;

export default function ConfidenceMeter({ score, routingStatus, compact = false }) {
  const { role } = useAuth();
  const numericScore = typeof score === 'number' ? score : Number(score) || 0;
  const isAutomated = numericScore > THRESHOLD || routingStatus === 'automated';
  const clampedScore = Math.min(100, Math.max(0, numericScore));

  // Hide numeric confidence and progress visuals for end users
  if (role === 'user') {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
        {isAutomated ? (
          <div className="flex items-center gap-2 rounded-lg bg-emerald-500/10 px-3 py-2 text-emerald-400">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span className="text-sm font-medium">Automated Assignment</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 rounded-lg bg-amber-500/10 px-3 py-2 text-amber-400">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span className="text-sm font-medium">Flagged for Manual Review</span>
          </div>
        )}
      </div>
    );
  }

  if (compact) {
    return (
      <div className="space-y-1">
        <div className="flex items-center justify-between text-xs">
          <span className={isAutomated ? 'text-emerald-400' : 'text-amber-400'}>
            {clampedScore.toFixed(1)}%
          </span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-slate-800">
          <div
            className={`h-full rounded-full ${isAutomated ? 'bg-emerald-500' : 'bg-amber-500'}`}
            style={{ width: `${clampedScore}%` }}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm font-medium text-slate-300">Model Confidence</span>
        <span className="text-2xl font-bold text-white">{clampedScore.toFixed(1)}%</span>
      </div>

      <div className="mb-4 h-3 overflow-hidden rounded-full bg-slate-800">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            isAutomated ? 'bg-emerald-500' : 'bg-amber-500'
          }`}
          style={{ width: `${clampedScore}%` }}
        />
      </div>

      {isAutomated ? (
        <div className="flex items-center gap-2 rounded-lg bg-emerald-500/10 px-3 py-2 text-emerald-400">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span className="text-sm font-medium">Automated Assignment</span>
        </div>
      ) : (
        <div className="flex items-center gap-2 rounded-lg bg-amber-500/10 px-3 py-2 text-amber-400">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span className="text-sm font-medium">Low Confidence – Flagged for Manual Review</span>
        </div>
      )}
    </div>
  );
}
