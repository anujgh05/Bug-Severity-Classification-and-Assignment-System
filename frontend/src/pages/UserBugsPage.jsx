import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext.jsx';
import { getUserBugs } from '../api/axios.js';

const STATUS_OPTIONS = [
  { label: 'All Status', value: '' },
  { label: 'Pending', value: 'pending' },
  { label: 'Resolved', value: 'resolved' },
];
const formatStatusLabel = (status) => {
  switch (status) {
    case 'pending':
      return 'Pending';
    case 'resolved':
      return 'Resolved';
    default:
      return status || 'Unknown';
  }
};

export default function UserBugsPage() {
  const { userId } = useAuth();
  const [bugs, setBugs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    if (!userId) return;
    setLoading(true);
    setError(null);
    getUserBugs(userId)
      .then((res) => setBugs(res.data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [userId]);

  if (!userId) {
    return (
      <div className="mx-auto max-w-3xl py-6">
        <p className="text-slate-400">
          Unable to load your bug history. Please sign out and sign in again.
        </p>
      </div>
    );
  }

  const visibleBugs = statusFilter
    ? bugs.filter((bug) => bug.bug_status === statusFilter)
    : bugs;

  return (
    <div className="mx-auto max-w-3xl py-6">
      <div className="mb-4 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">My Reported Bugs</h2>
          <p className="text-sm text-slate-400">Filter your reported bugs by current pending/resolved status.</p>
        </div>

        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <label htmlFor="status-filter" className="text-sm font-medium text-slate-300">
            Show:
          </label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          >
            {STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && <p className="text-slate-400">Loading...</p>}
      {error && <p className="text-red-400">{error}</p>}

      {!loading && visibleBugs.length === 0 && (
        <p className="text-slate-400">No reported bugs match the selected status.</p>
      )}

      <div className="space-y-4">
        {visibleBugs.map((b) => (
          <div key={b.bug_id} className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div className="max-w-3xl">
                <p className="text-sm text-slate-400">Ticket ID</p>
                <p className="text-lg font-bold text-white">#{b.bug_id}</p>
                <p className="mt-2 text-sm text-slate-300">{b.summary}</p>
                <p className="mt-3 text-sm leading-6 text-slate-400">{b.description}</p>
              </div>

              <div className="flex flex-col gap-2 sm:items-end">
                <div className="rounded-full bg-slate-800 px-3 py-1 text-sm font-semibold text-slate-200">
                  {formatStatusLabel(b.bug_status)}
                </div>
                <div className="rounded-2xl bg-slate-950/80 px-3 py-2 text-sm text-slate-300">
                  Assigned to: {b.assigned_developer_name || 'Unassigned'}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
