import { useCallback, useEffect, useMemo, useState } from 'react';
import { AlertTriangle, Loader2, RefreshCw, ShieldAlert, Users } from 'lucide-react';
import { getAdminBugs, adminOverrideBug, getDevelopers } from '../api/axios.js';
import ConfidenceMeter from './ConfidenceMeter.jsx';

const SEVERITY_OPTIONS = ['Low', 'Medium', 'High'];

const normalizeSeverityOption = (severity) => {
  if (!severity) return 'Medium';
  const value = String(severity).toLowerCase();
  if (value.includes('high')) return 'High';
  if (value.includes('medium')) return 'Medium';
  if (value.includes('low')) return 'Low';
  return 'Medium';
};

function SeverityBadge({ severity }) {
  const label = severity || 'Unknown';
  const tone =
    label.includes('High')
      ? 'bg-red-500/15 text-red-300 border-red-500/30'
      : label.includes('Medium')
        ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
        : 'bg-sky-500/15 text-sky-300 border-sky-500/30';

  return (
    <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${tone}`}>
      {label}
    </span>
  );
}

function RoutingPill({ status }) {
  const text = status || 'pending_review';
  const isFlagged = text === 'pending_review';

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2 py-1 text-[11px] font-medium ${
        isFlagged
          ? 'border-amber-500/30 bg-amber-500/10 text-amber-300'
          : 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
      }`}
    >
      {isFlagged && <AlertTriangle className="h-3 w-3" />}
      {text}
    </span>
  );
}

function BugPanel({
  title,
  subtitle,
  color,
  bugs,
  developers,
  selections,
  assigneeSelections,
  submittingId,
  setSelections,
  setAssigneeSelections,
  handleOverride,
}) {
  const borderColor =
    color === 'amber'
      ? 'border-amber-500/30 bg-amber-500/5'
      : 'border-emerald-500/30 bg-emerald-500/5';

  const labelColor =
    color === 'amber'
      ? 'text-amber-300 border-amber-500/30 bg-amber-500/10'
      : 'text-emerald-300 border-emerald-500/30 bg-emerald-500/10';

  return (
    <div className={`rounded-2xl border p-4 ${borderColor}`}>
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <h3 className="text-xl font-semibold text-white">{title}</h3>
          <p className="text-base text-slate-400">{subtitle}</p>
        </div>
        <span className={`rounded-full border px-2.5 py-1 text-xs font-medium ${labelColor}`}>
          {bugs.length} bugs
        </span>
      </div>

      {bugs.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900/40 p-8 text-center text-sm text-slate-500">
          No bugs in this queue.
        </div>
      ) : (
        <div className="space-y-4">
          {bugs.map((bug) => {
            const currentSeverity = selections[bug.bug_id] ?? normalizeSeverityOption(bug.severity);
            return (
              <div key={bug.bug_id} className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
                <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                  <div className="min-w-0 flex-1">
                    <div className="mb-3 flex flex-wrap items-center gap-2">
                      <span className="rounded-full border border-slate-700 bg-slate-950 px-2 py-1 font-mono text-xs text-slate-300">
                        #{bug.bug_id}
                      </span>
                      <SeverityBadge severity={bug.severity} />
                      <RoutingPill status={bug.routing_status} />
                    </div>

                    <h4 className="text-xl font-semibold text-white">{bug.summary}</h4>
                    <p className="mt-2 max-w-3xl text-[15px] leading-6 text-slate-400">{bug.description}</p>
                  </div>

                  <div className="w-full xl:max-w-[300px]">
                    <ConfidenceMeter
                      score={bug.max_confidence}
                      routingStatus={bug.routing_status}
                      compact
                    />
                  </div>
                </div>

                <div className="mt-4 grid gap-3 xl:grid-cols-[1.1fr_1.1fr_1.2fr_auto] xl:items-end">
                  <div>
                    <label className="mb-1 block text-xs uppercase tracking-wide text-slate-400">
                      Assigned developer
                    </label>
                    <select
                      value={assigneeSelections[bug.bug_id] ?? ''}
                      onChange={(e) =>
                        setAssigneeSelections((prev) => ({
                          ...prev,
                          [bug.bug_id]: e.target.value,
                        }))
                      }
                      className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none transition focus:border-indigo-500"
                    >
                      <option value="">Unassigned</option>
                      {developers.map((dev) => (
                        <option key={dev.developer_id} value={dev.developer_id}>
                          {dev.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="mb-1 block text-xs uppercase tracking-wide text-slate-400">
                      Severity override
                    </label>
                    <select
                      value={currentSeverity}
                      onChange={(e) =>
                        setSelections((prev) => ({ ...prev, [bug.bug_id]: e.target.value }))
                      }
                      className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none transition focus:border-indigo-500"
                    >
                      {SEVERITY_OPTIONS.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="min-w-0">
                    <label className="mb-1 block text-xs uppercase tracking-wide text-slate-400">
                      Current assignee
                    </label>
                    <div className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-[15px] text-slate-200">
                      {bug.assigned_developer_name || 'Unassigned'}
                    </div>
                  </div>

                  <button
                    type="button"
                    disabled={submittingId === bug.bug_id}
                    onClick={() => handleOverride(bug.bug_id)}
                    className="rounded-xl bg-indigo-600 px-4 py-2.5 text-[15px] font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {submittingId === bug.bug_id ? 'Updating...' : 'Apply'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function TriageTable() {
  const [bugs, setBugs] = useState([]);
  const [developers, setDevelopers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selections, setSelections] = useState({});
  const [assigneeSelections, setAssigneeSelections] = useState({});
  const [submittingId, setSubmittingId] = useState(null);

  const fetchAdminData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [bugsRes, developersRes] = await Promise.all([getAdminBugs(), getDevelopers()]);
      const bugData = bugsRes.data;
      setBugs(bugData);
      setDevelopers(developersRes.data || []);

      const severityDefaults = {};
      const assignmentDefaults = {};
      bugData.forEach((bug) => {
        severityDefaults[bug.bug_id] = normalizeSeverityOption(bug.severity);
        assignmentDefaults[bug.bug_id] = bug.assigned_developer_id ?? '';
      });
      setSelections(severityDefaults);
      setAssigneeSelections(assignmentDefaults);
    } catch (err) {
      setError(err.message || 'Failed to load admin dashboard data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAdminData();
  }, [fetchAdminData]);

  const sortedBugs = useMemo(() => {
    return [...bugs].sort((a, b) => {
      const flaggedDiff = Number(b.routing_status === 'pending_review') - Number(a.routing_status === 'pending_review');
      if (flaggedDiff !== 0) return flaggedDiff;
      return Number(b.confidence_score || 0) - Number(a.confidence_score || 0);
    });
  }, [bugs]);

  const flaggedBugs = sortedBugs.filter((bug) => bug.routing_status === 'pending_review');
  const automatedBugs = sortedBugs.filter((bug) => bug.routing_status === 'automated');
  const flaggedCount = flaggedBugs.length;
  const automatedCount = automatedBugs.length;

  const handleOverride = async (bugId) => {
    setSubmittingId(bugId);
    try {
      await adminOverrideBug(bugId, {
        severity: selections[bugId],
        assigned_developer_id:
          assigneeSelections[bugId] === '' ? null : Number(assigneeSelections[bugId]),
      });
      await fetchAdminData();
    } catch (err) {
      setError(err.message || 'Unable to update bug.');
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
    <div className="space-y-5">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Admin Cockpit</h2>
          <p className="text-base text-slate-400">
            Review flagged bugs first, then resolve severity and assignment decisions.
          </p>
        </div>
        <button
          type="button"
          onClick={fetchAdminData}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200 transition hover:bg-slate-800"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4">
          <div className="text-sm uppercase tracking-wide text-amber-300">Flagged</div>
          <div className="mt-2 text-4xl font-bold text-white">{flaggedCount}</div>
        </div>
        <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4">
          <div className="text-sm uppercase tracking-wide text-emerald-300">Automated</div>
          <div className="mt-2 text-4xl font-bold text-white">{automatedCount}</div>
        </div>
        <div className="rounded-2xl border border-slate-700 bg-slate-900/70 p-4">
          <div className="text-sm uppercase tracking-wide text-slate-400">Total</div>
          <div className="mt-2 text-4xl font-bold text-white">{bugs.length}</div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
        <div className="mb-3 flex items-center gap-2 text-sm text-slate-300">
          <Users className="h-4 w-4 text-indigo-400" />
          <span className="font-semibold">Developer Workload</span>
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {developers.map((developer) => (
            <div key={developer.developer_id} className="rounded-xl border border-slate-800 bg-slate-950/70 p-3">
              <p className="text-sm font-semibold text-white">{developer.name}</p>
              <p className="mt-1 text-xs text-slate-400">{developer.email}</p>
              <p className="mt-3 text-sm text-indigo-300">Current workload: {developer.current_workload || 0}</p>
            </div>
          ))}
        </div>
      </div>

      {bugs.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-slate-700 bg-slate-900/50 py-16 text-slate-500">
          <ShieldAlert className="h-8 w-8" />
          <p>No bugs found.</p>
        </div>
      ) : (
        <div className="space-y-6">
          <BugPanel
            title="Flagged for review"
            subtitle="Manual attention required"
            color="amber"
            bugs={flaggedBugs}
            developers={developers}
            selections={selections}
            assigneeSelections={assigneeSelections}
            submittingId={submittingId}
            setSelections={setSelections}
            setAssigneeSelections={setAssigneeSelections}
            handleOverride={handleOverride}
          />
          <BugPanel
            title="Automated / routed"
            subtitle="Confidence is strong enough to proceed"
            color="emerald"
            bugs={automatedBugs}
            developers={developers}
            selections={selections}
            assigneeSelections={assigneeSelections}
            submittingId={submittingId}
            setSelections={setSelections}
            setAssigneeSelections={setAssigneeSelections}
            handleOverride={handleOverride}
          />
        </div>
      )}
    </div>
  );
}
