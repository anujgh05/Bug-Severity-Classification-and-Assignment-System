import { useCallback, useEffect, useState } from 'react';
import { Loader2, Inbox, Users } from 'lucide-react';
import { getDeveloperTasks, updateDeveloperBugStatus } from '../api/axios.js';
import { useAuth } from '../context/AuthContext.jsx';
import ConfidenceMeter from './ConfidenceMeter.jsx';

function SeverityBadge({ severity }) {
  const label = severity || 'Unclassified';
  const tone = label.includes('High')
    ? 'bg-red-500/15 text-red-400'
    : label.includes('Medium')
      ? 'bg-amber-500/15 text-amber-400'
      : 'bg-sky-500/15 text-sky-400';

  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${tone}`}>
      {label}
    </span>
  );
}

export default function DevBoard() {
  const { developerId } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingId, setUpdatingId] = useState(null);

  const fetchTasks = useCallback(async () => {
    if (!developerId) return;
    setLoading(true);
    setError(null);
    try {
      const { data } = await getDeveloperTasks(developerId);
      setTasks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [developerId]);

  const handleStatusChange = async (bugId, newStatus) => {
    if (!developerId) return;
    setUpdatingId(bugId);
    setError(null);
    try {
      await updateDeveloperBugStatus(developerId, bugId, newStatus);
      await fetchTasks();
    } catch (err) {
      setError(err.message);
    } finally {
      setUpdatingId(null);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-slate-400">
        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
        Loading assigned tasks...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white">Developer Task Board</h2>
        <p className="text-sm text-slate-400">
          Auto-assigned tickets via Cosine Similarity matching (Developer #{developerId})
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {tasks.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-slate-700 py-16 text-slate-500">
          <Inbox className="h-8 w-8" />
          <p>No tasks assigned yet.</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {tasks.map((task) => (
            <article
              key={task.bug_id}
              className="rounded-xl border border-slate-800 bg-slate-900 p-5 transition-colors hover:border-slate-700"
            >
              <div className="mb-3 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="font-mono text-xs text-slate-500">#{task.bug_id}</p>
                  <div className="mt-1 flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-white">{task.summary}</h3>
                    <SeverityBadge severity={task.severity} />
                  </div>
                </div>
                <div className="flex flex-col items-start gap-2">
                  <span className="rounded-full bg-slate-800 px-3 py-1 text-sm font-semibold text-slate-200">
                    {task.bug_status === 'resolved' ? 'Resolved' : 'Pending'}
                  </span>
                  <select
                    value={task.bug_status || 'pending'}
                    onChange={(e) => handleStatusChange(task.bug_id, e.target.value)}
                    disabled={updatingId === task.bug_id}
                    className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="pending">Pending</option>
                    <option value="resolved">Resolved</option>
                  </select>
                </div>
              </div>

              <p className="mb-4 line-clamp-3 text-sm text-slate-400">{task.description}</p>

              <div className="grid gap-3 sm:grid-cols-2">
                {task.max_confidence != null && (
                  <ConfidenceMeter
                    score={task.max_confidence}
                    routingStatus={task.routing_status}
                  />
                )}
                {task.similarity_score != null && (
                  <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950 p-4">
                    <Users className="h-5 w-5 text-indigo-400" />
                    <div>
                      <p className="text-xs text-slate-500">Match Score</p>
                      <p className="text-lg font-bold text-indigo-300">
                        {task.similarity_score.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
