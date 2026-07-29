import { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { submitBug } from '../api/axios.js';
import ConfidenceMeter from './ConfidenceMeter.jsx';

export default function BugForm() {
  const [formData, setFormData] = useState({ summary: '', description: '' });
  const [loading, setLoading] = useState(false);
  const [ticketResponse, setTicketResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setTicketResponse(null);

    try {
      const { data } = await submitBug(formData.summary, formData.description);
      setTicketResponse(data);
      setFormData({ summary: '', description: '' });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="summary" className="mb-2 block text-sm font-medium text-slate-300">
            Bug Summary
          </label>
          <input
            id="summary"
            name="summary"
            type="text"
            value={formData.summary}
            onChange={handleChange}
            required
            placeholder="e.g., Database connection timeout on login"
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-white placeholder-slate-500 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label htmlFor="description" className="mb-2 block text-sm font-medium text-slate-300">
            Detailed Description
          </label>
          <textarea
            id="description"
            name="description"
            rows={6}
            value={formData.description}
            onChange={handleChange}
            required
            placeholder="Describe the bug in detail..."
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-white placeholder-slate-500 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Send className="h-4 w-4" />
              Submit Bug Report
            </>
          )}
        </button>
      </form>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-white">Submission Result</h3>

        {!ticketResponse && !loading && (
          <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900/50 p-8 text-center text-slate-500">
            Submit a bug report to see routing feedback here.
          </div>
        )}

        {ticketResponse && (
          <div className="space-y-4">
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
              <p className="text-sm text-slate-400">Ticket ID</p>
              <p className="text-xl font-bold text-white">#{ticketResponse.bug_id}</p>
              <p className="mt-3 text-sm text-slate-400">Predicted Severity</p>
              <p className="font-medium text-indigo-300">{ticketResponse.predicted_class}</p>
            </div>

            <ConfidenceMeter
              score={ticketResponse.max_confidence}
              routingStatus={ticketResponse.routing_status}
            />

            {ticketResponse.assigned_developer_id && (
              <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-sm text-emerald-300">
                Automatically assigned to Developer #{ticketResponse.assigned_developer_id}
                {ticketResponse.similarity_score != null && (
                  <span> (Similarity: {ticketResponse.similarity_score}%)</span>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
