import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, User, Code2, ArrowRight } from 'lucide-react';
import { useAuth, ROLES } from '../context/AuthContext.jsx';

const roleCards = [
  {
    id: 'user',
    icon: User,
    title: 'End User Portal',
    badge: 'Submit Reports',
    color: 'indigo',
    description: 'Submit software bug reports.',
    loginPath: '/login/user',
    accentClass: 'hover:border-indigo-500 hover:shadow-indigo-500/10',
    iconBg: 'bg-indigo-600/20 text-indigo-400 group-hover:bg-indigo-600 group-hover:text-white',
    btnBg: 'bg-indigo-600/10 text-indigo-400 group-hover:bg-indigo-600 group-hover:text-white',
  },
  {
    id: 'admin',
    icon: Shield,
    title: 'Admin Portal',
    badge: 'Manual Review',
    color: 'amber',
    description: 'Supervisory portal for review.',
    loginPath: '/login/admin',
    accentClass: 'hover:border-amber-500 hover:shadow-amber-500/10',
    iconBg: 'bg-amber-500/20 text-amber-400 group-hover:bg-amber-500 group-hover:text-white',
    btnBg: 'bg-amber-500/10 text-amber-400 group-hover:bg-amber-500 group-hover:text-white',
  },
  {
    id: 'developer',
    icon: Code2,
    title: 'Developer Portal',
    badge: 'Task Board',
    color: 'sky',
    description: 'View assigned tickets.',
    loginPath: '/login/developer',
    accentClass: 'hover:border-sky-500 hover:shadow-sky-500/10',
    iconBg: 'bg-sky-500/20 text-sky-400 group-hover:bg-sky-500 group-hover:text-white',
    btnBg: 'bg-sky-500/10 text-sky-400 group-hover:bg-sky-500 group-hover:text-white',
  },
];

export default function LoginPage() {
  const { isAuthenticated, role } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated && role && ROLES[role]) {
      navigate(ROLES[role].defaultPath, { replace: true });
    }
  }, [isAuthenticated, role, navigate]);

  return (
    <div className="mx-auto max-w-5xl py-4">
      <div className="mb-10 text-center">
        <h2 className="mt-3 text-3xl font-extrabold text-white sm:text-4xl">
          Select Login Portal
        </h2>
        <p className="mx-auto mt-2 max-w-xl text-sm text-slate-400 sm:text-base">
          Choose your role below to navigate to the dedicated login portal.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {roleCards.map(
          ({ id, icon: Icon, title, badge, description, loginPath, accentClass, iconBg, btnBg }) => (
            <Link
              key={id}
              to={loginPath}
              className={`group flex flex-col justify-between rounded-2xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl transition-all duration-200 ${accentClass}`}
            >
              <div>
                <div className="mb-4 flex items-center justify-between">
                  <div className={`rounded-xl p-3 transition-colors ${iconBg}`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <span className="rounded-full bg-slate-800 px-2.5 py-0.5 text-xs font-medium text-slate-300">
                    {badge}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-white">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">{description}</p>
              </div>

              <div className="mt-6 flex items-center justify-between border-t border-slate-800/80 pt-4">
                <span className="text-xs font-semibold text-slate-400 group-hover:text-slate-200">
                  Open Login Page
                </span>
                <div className={`rounded-lg p-2 transition-colors ${btnBg}`}>
                  <ArrowRight className="h-4 w-4" />
                </div>
              </div>
            </Link>
          ),
        )}
      </div>
    </div>
  );
}
