import { useCallback, useEffect, useState } from 'react';
import { RefreshCw, Loader2, ShieldAlert, Users } from 'lucide-react';
import { getAdminBugs, adminOverrideBug, getDevelopers } from '../api/axios.js';
import ConfidenceMeter from './ConfidenceMeter.jsx';

const SEVERITY_OPTIONS = ['Low', 'Medium', 'High'];

const normalizeSeverityOption = (severity) => {
  if (!severity) return 'Medium';
  if (severity.toLowerCase().includes('high')) return 'High';
  if (severity.toLowerCase().includes('medium')) return 'Medium';
  if (severity.toLowerCase().includes('low')) return 'Low';
  return 'Medium';
};

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
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAdminData();
  }, [fetchAdminData]);

  const handleOverride = async (bugId) => {
    setSubmittingId(bugId);
    try {
      await adminOverrideBug(bugId, {
        severity: selections[bugId],
        assigned_developer_id:
          assigneeSelections[bugId] === ''
            ? null
            : Number(assigneeSelections[bugId]),
      });
      await fetchAdminData();
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
          <h2 className="text-xl font-semibold text-white">Admin Cockpit</h2>
          <p className="text-sm text-slate-400">
            Review all bugs, override severity labels, and manage developer assignment/workload
          </p>
        </div>
        <button
          type="button"
          onClick={fetchAdminData}
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

      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <div className="flex items-center gap-2 text-sm text-slate-300">
          <Users className="h-4 w-4 text-indigo-400" />
          <span className="font-medium">Developer Workload</span>
        </div>
        <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {developers.map((developer) => (
            <div key={developer.developer_id} className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
              <p className="text-sm font-semibold text-white">{developer.name}</p>
              <p className="mt-1 text-xs text-slate-400">{developer.email}</p>
              <p className="mt-2 text-sm text-indigo-300">Current workload: {developer.current_workload || 0}</p>
            </div>
          ))}
        </div>
      </div>

      {bugs.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-slate-700 py-16 text-slate-500">
          <ShieldAlert className="h-8 w-8" />
          <p>No bugs found.</p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-slate-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900 text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Summary</th>
                <th className="px-4 py-3 font-medium">Severity</th>
                <th className="px-4 py-3 font-medium">Confidence</th>
                <th className="px-4 py-3 font-medium">Routing</th>
                <th className="px-4 py-3 font-medium">Assigned Dev</th>
                <th className="px-4 py-3 font-medium">Reassign</th>
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
                    <SeverityBadge severity={bug.severity} />
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
                    <span className="text-sm text-slate-300">{bug.routing_status || 'pending_review'}</span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-sm text-slate-300">
                      {bug.assigned_developer_name || 'Unassigned'}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <select
                      value={assigneeSelections[bug.bug_id] ?? ''}
                      onChange={(e) =>
                        setAssigneeSelections((prev) => ({
                          ...prev,
                          [bug.bug_id]: e.target.value,
                        }))
                      }
                      className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-indigo-500"
                    >
                      <option value="">Unassigned</option>
                      {developers.map((dev) => (
                        <option key={dev.developer_id} value={dev.developer_id}>
                          {dev.name}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-4 py-4">
                    {(() => {
                      const currentSeverity = selections[bug.bug_id] ?? normalizeSeverityOption(bug.severity);
                      return (
                        <select
                          value={currentSeverity}
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
                      );
                    })()}
                  </td>
                  <td className="px-4 py-4">
                    <button
                      type="button"
                      disabled={submittingId === bug.bug_id}
                      onClick={() => handleOverride(bug.bug_id)}
                      className="whitespace-nowrap rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-60"
                    >
                      {submittingId === bug.bug_id ? 'Updating...' : 'Apply'}
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
