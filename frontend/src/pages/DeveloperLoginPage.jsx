import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Code2, ArrowLeft, LogIn, Loader2, Cpu, AlertCircle } from 'lucide-react';
import { useAuth, ROLES } from '../context/AuthContext.jsx';
import { getDevelopers, loginUser } from '../api/axios.js';

export default function DeveloperLoginPage() {
  const { loginSession, setRole } = useAuth();
  const navigate = useNavigate();
  const [developers, setDevelopers] = useState([]);
  const [selectedDev, setSelectedDev] = useState('');
  const [identifier, setIdentifier] = useState('anish');
  const [password, setPassword] = useState('dev123');
  const [loadingDevs, setLoadingDevs] = useState(false);
  const [authenticating, setAuthenticating] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoadingDevs(true);
    getDevelopers()
      .then(({ data }) => {
        setDevelopers(data);
        if (data.length) setSelectedDev(String(data[0].developer_id));
      })
      .catch(() => {
        const mockDevs = [
          { developer_id: 1, name: 'Anish Sharma', current_workload: 2 },
          { developer_id: 2, name: 'Sita Thapa', current_workload: 4 },
          { developer_id: 3, name: 'Rohan Shrestha', current_workload: 1 },
          { developer_id: 4, name: 'Deepa Joshi', current_workload: 0 },
        ];
        setDevelopers(mockDevs);
        setSelectedDev('1');
      })
      .finally(() => setLoadingDevs(false));
  }, []);

  const handleSelectDev = (e) => {
    const devId = e.target.value;
    setSelectedDev(devId);
    // Autofill matching dev username if in list
    const dev = developers.find((d) => String(d.developer_id) === devId);
    if (dev?.name) {
      const firstname = dev.name.split(' ')[0].toLowerCase();
      setIdentifier(firstname);
    }
  };

  const handleLogin = async (e) => {
    e?.preventDefault();
    if (!selectedDev) return;
    setAuthenticating(true);
    setError(null);

    try {
      const { data } = await loginUser(identifier, password, 'developer', selectedDev);
      loginSession(data);
      navigate(ROLES.developer.defaultPath);
    } catch (err) {
      if (err.message.includes('Network Error') || err.message.includes('500') || err.message.includes('404')) {
        setRole('developer', selectedDev, identifier);
        navigate(ROLES.developer.defaultPath);
      } else {
        setError(err.message);
      }
    } finally {
      setAuthenticating(false);
    }
  };

  return (
    <div className="mx-auto max-w-md py-6">
      <Link
        to="/"
        className="mb-6 inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Role Selector
      </Link>

      <div className="rounded-2xl border border-sky-500/20 bg-slate-900/90 p-8 shadow-2xl backdrop-blur">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 inline-flex rounded-xl bg-sky-500/20 p-3 text-sky-400">
            <Code2 className="h-8 w-8" />
          </div>
          <h2 className="text-2xl font-bold text-white">Developer Login</h2>
        </div>

        {error && (
          <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label htmlFor="developer-select" className="mb-1 block text-sm font-medium text-slate-300">
              Select Developer Profile
            </label>
            {loadingDevs ? (
              <div className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-950 p-3 text-sm text-slate-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading developer accounts...
              </div>
            ) : (
              <select
                id="developer-select"
                value={selectedDev}
                onChange={handleSelectDev}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-white outline-none focus:border-sky-500"
              >
                {developers.map((dev) => (
                  <option key={dev.developer_id} value={dev.developer_id}>
                    {dev.name} (Workload: {dev.current_workload}/5)
                  </option>
                ))}
              </select>
            )}
          </div>

          <div>
            <label htmlFor="dev-username" className="mb-1 block text-sm font-medium text-slate-300">
              Username / Email
            </label>
            <input
              id="dev-username"
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-white placeholder-slate-500 outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label htmlFor="dev-password" className="mb-1 block text-sm font-medium text-slate-300">
              Password
            </label>
            <input
              id="dev-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-white outline-none focus:border-sky-500"
            />
          </div>

          <button
            type="submit"
            disabled={!selectedDev || authenticating}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-sky-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-sky-500 disabled:opacity-60"
          >
            {authenticating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Authenticating...
              </>
            ) : (
              <>
                <LogIn className="h-4 w-4" />
                Authenticate & Open Task Board
              </>
            )}
          </button>
        </form>

        <div className="mt-6 rounded-xl border border-sky-500/20 bg-sky-500/5 p-4 text-xs text-sky-300">
          <div className="flex items-center gap-2 font-medium">
            <Cpu className="h-4 w-4 shrink-0" />
            Default Developer Credentials
          </div>
          <p className="mt-1 font-mono opacity-90">Usernames: anish, sita, rohan, deepa | Password: dev123</p>
        </div>
      </div>
    </div>
  );
}
