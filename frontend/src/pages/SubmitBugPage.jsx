import BugForm from '../components/BugForm.jsx';

export default function SubmitBugPage() {
  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white">Submit a Bug Report</h2>
        <p className="mt-1 text-slate-400">
          Report issues for automated SVM severity classification and routing.
        </p>
      </div>
      <BugForm />
    </div>
  );
}
