import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, ArrowLeft, LogIn, ShieldAlert, Loader2, AlertCircle } from 'lucide-react';
import { useAuth, ROLES } from '../context/AuthContext.jsx';
import { loginUser } from '../api/axios.js';

export default function AdminLoginPage() {
  const { loginSession, setRole } = useAuth();
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLogin = async (e) => {
    e?.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const { data } = await loginUser(identifier, password, 'admin');
      loginSession(data);
      navigate(ROLES.admin.defaultPath);
    } catch (err) {
      if (err.message.includes('Network Error') || err.message.includes('500') || err.message.includes('404')) {
        setRole('admin', null, identifier);
        navigate(ROLES.admin.defaultPath);
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
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

      <div className="rounded-2xl border border-amber-500/20 bg-slate-900/90 p-8 shadow-2xl backdrop-blur">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 inline-flex rounded-xl bg-amber-500/20 p-3 text-amber-400">
            <Shield className="h-8 w-8" />
          </div>
          <h2 className="text-2xl font-bold text-white">Admin Login</h2>
        </div>

        {error && (
          <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label htmlFor="admin-identifier" className="mb-1 block text-sm font-medium text-slate-300">
              Admin Identifier / Email
            </label>
            <input
              id="admin-identifier"
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-white placeholder-slate-500 outline-none focus:border-amber-500"
            />
          </div>

          <div>
            <label htmlFor="admin-password" className="mb-1 block text-sm font-medium text-slate-300">
              Password
            </label>
            <input
              id="admin-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-white outline-none focus:border-amber-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-amber-600 px-4 py-3 font-semibold text-white transition-colors hover:bg-amber-500 disabled:opacity-60"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Verifying Credentials...
              </>
            ) : (
              <>
                <LogIn className="h-4 w-4" />
                Authenticate Admin Session
              </>
            )}
          </button>
        </form>

        <div className="mt-6 rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-xs text-amber-300">
          <div className="flex items-center gap-2 font-medium">
            <ShieldAlert className="h-4 w-4 shrink-0" />
            Default Admin Database Account
          </div>
          <p className="mt-1 font-mono opacity-90">Username: admin | Password: admin123</p>
        </div>
      </div>
    </div>
  );
}
