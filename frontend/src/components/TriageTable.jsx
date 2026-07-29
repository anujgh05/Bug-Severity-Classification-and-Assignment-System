import { useCallback, useEffect, useState } from 'react';
import { RefreshCw, Loader2, ShieldAlert } from 'lucide-react';
import { getPendingBugs, overrideBug } from '../api/axios.js';
import ConfidenceMeter from './ConfidenceMeter.jsx';

const SEVERITY_OPTIONS = ['Low', 'Medium', 'High'];

function SeverityBadge({ severity }) {
  const label = severity || 'Unknown';
  const tone =
    label.includes('High')
      ? 'bg-red-500/15 text-red-400 border-red-500/30'
      : label.includes('Medium')
        ? 'bg-amber-500/15 text-amber-400 border-amber-500/30'
        : 'bg-sky-500/15 text-sky-400 border-sky-500/30';

  return (
    <span className={`inline-flex rounded-full border px-2.5 py-0.5 text-xs font-medium ${tone}`}>
      {label}
    </span>
  );
}

export default function TriageTable() {
  const [bugs, setBugs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selections, setSelections] = useState({});
  const [submittingId, setSubmittingId] = useState(null);

  const fetchPending = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await getPendingBugs();
      setBugs(data);
      const defaults = {};
      data.forEach((bug) => {
        defaults[bug.bug_id] = 'Medium';
      });
      setSelections(defaults);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPending();
  }, [fetchPending]);

  const handleOverride = async (bugId) => {
    setSubmittingId(bugId);
    try {
      await overrideBug(bugId, selections[bugId]);
      await fetchPending();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmittingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-slate-400">
        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
        Loading pending reviews...
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Pending Manual Triage</h2>
          <p className="text-sm text-slate-400">
            Bugs below the 55% confidence threshold awaiting admin override
          </p>
        </div>
        <button
          type="button"
          onClick={fetchPending}
          className="flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {bugs.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-slate-700 py-16 text-slate-500">
          <ShieldAlert className="h-8 w-8" />
          <p>No bugs pending manual review.</p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-slate-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900 text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Summary</th>
                <th className="px-4 py-3 font-medium">Confidence</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Override Severity</th>
                <th className="px-4 py-3 font-medium">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 bg-slate-950/50">
              {bugs.map((bug) => (
                <tr key={bug.bug_id} className="align-top">
                  <td className="px-4 py-4 font-mono text-slate-300">#{bug.bug_id}</td>
                  <td className="px-4 py-4">
                    <p className="font-medium text-white">{bug.summary}</p>
                    <p className="mt-1 line-clamp-2 text-xs text-slate-500">{bug.description}</p>
                  </td>
                  <td className="px-4 py-4">
                    <div className="w-24">
                      <ConfidenceMeter
                        score={bug.max_confidence}
                        routingStatus={bug.routing_status}
                        compact
                      />
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <SeverityBadge severity={bug.predicted_severity} />
                  </td>
                  <td className="px-4 py-4">
                    <select
                      value={selections[bug.bug_id] || 'Medium'}
                      onChange={(e) =>
                        setSelections((prev) => ({ ...prev, [bug.bug_id]: e.target.value }))
                      }
                      className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-indigo-500"
                    >
                      {SEVERITY_OPTIONS.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-4 py-4">
                    <button
                      type="button"
                      disabled={submittingId === bug.bug_id}
                      onClick={() => handleOverride(bug.bug_id)}
                      className="whitespace-nowrap rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-60"
                    >
                      {submittingId === bug.bug_id ? 'Allocating...' : 'Confirm & Allocate Developer'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
