import TriageTable from '../components/TriageTable.jsx';

export default function AdminTriagePage() {
  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
        <h2 className="text-2xl font-bold text-white">Admin Supervisory Cockpit</h2>
        <p className="mt-2 max-w-3xl text-sm text-slate-400">
          Review low-confidence predictions first, verify severity manually, and route each bug to the right developer without crowding the queue.
        </p>
      </div>
      <TriageTable />
    </div>
  );
}
