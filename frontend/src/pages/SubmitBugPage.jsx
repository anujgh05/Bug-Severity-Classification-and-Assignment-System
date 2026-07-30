import BugForm from '../components/BugForm.jsx';

export default function SubmitBugPage() {
  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white">Submit a Bug Report</h2>
      </div>
      <BugForm />
    </div>
  );
}
