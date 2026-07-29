import TriageTable from '../components/TriageTable.jsx';

export default function AdminTriagePage() {
  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white">Admin Supervisory Cockpit</h2>
        <p className="mt-1 text-slate-400">
          Review low-confidence predictions and manually confirm severity before developer allocation.
        </p>
      </div>
      <TriageTable />
    </div>
  );
}
