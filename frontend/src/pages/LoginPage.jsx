import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, User, Code2, Loader2 } from 'lucide-react';
import { useAuth, ROLES } from '../context/AuthContext.jsx';
import { getDevelopers } from '../api/axios.js';

const roleCards = [
  {
    id: 'user',
    icon: User,
    title: 'End User',
    description: 'Submit bug reports without seeing internal ML metrics in the workflow.',
    path: ROLES.user.defaultPath,
  },
  {
    id: 'admin',
    icon: Shield,
    title: 'Admin',
    description: 'Supervisory cockpit for manual triage and developer allocation overrides.',
    path: ROLES.admin.defaultPath,
  },
  {
    id: 'developer',
    icon: Code2,
    title: 'Developer',
    description: 'View auto-assigned tasks based on cosine similarity expertise matching.',
    path: ROLES.developer.defaultPath,
  },
];

export default function LoginPage() {
  const { setRole, isAuthenticated, role } = useAuth();
  const navigate = useNavigate();
  const [developers, setDevelopers] = useState([]);
  const [selectedDev, setSelectedDev] = useState('');
  const [loadingDevs, setLoadingDevs] = useState(false);

  useEffect(() => {
    if (isAuthenticated && role) {
      navigate(ROLES[role].defaultPath, { replace: true });
    }
  }, [isAuthenticated, role, navigate]);

  useEffect(() => {
    setLoadingDevs(true);
    getDevelopers()
      .then(({ data }) => {
        setDevelopers(data);
        if (data.length) setSelectedDev(String(data[0].developer_id));
      })
      .catch(() => {})
      .finally(() => setLoadingDevs(false));
  }, []);

  const handleSelect = (roleId) => {
    if (roleId === 'developer') {
      if (!selectedDev) return;
      setRole('developer', selectedDev);
      navigate(ROLES.developer.defaultPath);
      return;
    }
    setRole(roleId);
    navigate(ROLES[roleId].defaultPath);
  };

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-10 text-center">
        <h2 className="text-3xl font-bold text-white">Select Your Role</h2>
        <p className="mt-2 text-slate-400">
          Role-based access control for the 3-tier SVM bug triage system
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {roleCards.map(({ id, icon: Icon, title, description }) => (
          <button
            key={id}
            type="button"
            onClick={() => handleSelect(id)}
            className="group rounded-xl border border-slate-800 bg-slate-900 p-6 text-left transition-all hover:border-indigo-500 hover:shadow-lg hover:shadow-indigo-500/10"
          >
            <div className="mb-4 inline-flex rounded-lg bg-indigo-600/20 p-3 text-indigo-400 group-hover:bg-indigo-600 group-hover:text-white">
              <Icon className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-semibold text-white">{title}</h3>
            <p className="mt-2 text-sm text-slate-400">{description}</p>
          </button>
        ))}
      </div>

      <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900 p-5">
        <label htmlFor="developer-select" className="mb-2 block text-sm font-medium text-slate-300">
          Developer profile (required for Developer role)
        </label>
        {loadingDevs ? (
          <div className="flex items-center gap-2 text-slate-400">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading developers...
          </div>
        ) : (
          <select
            id="developer-select"
            value={selectedDev}
            onChange={(e) => setSelectedDev(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-white outline-none focus:border-indigo-500"
          >
            {developers.map((dev) => (
              <option key={dev.developer_id} value={dev.developer_id}>
                {dev.name} — workload: {dev.current_workload}/5
              </option>
            ))}
          </select>
        )}
      </div>
    </div>
  );
}
