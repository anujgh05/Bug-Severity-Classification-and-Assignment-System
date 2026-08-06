import { NavLink, useNavigate } from 'react-router-dom';
import { Bug, LayoutDashboard, ListTodo, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';

const navLinkClass = ({ isActive }) =>
  `flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
    isActive ? 'bg-indigo-600 text-white' : 'text-slate-300 hover:bg-slate-800 hover:text-white'
  }`;

export default function Layout({ children }) {
  const { role, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
        <div className="flex w-full items-center justify-between px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-indigo-600 p-2">
              <Bug className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold">Bug Triage</h1>
            </div>
          </div>

          {isAuthenticated && (
            <nav className="flex items-center gap-2">
              {role === 'user' && (
                <>
                  <NavLink to="/submit-bug" className={navLinkClass}>
                    Submit Bug
                  </NavLink>
                  <NavLink to="/user/my-bugs" className={navLinkClass}>
                    My Bugs
                  </NavLink>
                </>
              )}
              {role === 'admin' && (
                <NavLink to="/admin/triage" className={navLinkClass}>
                  <LayoutDashboard className="h-4 w-4" />
                  Triage Cockpit
                </NavLink>
              )}
              {role === 'developer' && (
                <NavLink to="/developer/my-tasks" className={navLinkClass}>
                  <ListTodo className="h-4 w-4" />
                  My Tasks
                </NavLink>
              )}
              <button
                type="button"
                onClick={handleLogout}
                className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-400 hover:bg-slate-800 hover:text-white"
              >
                <LogOut className="h-4 w-4" />
                Switch Role
              </button>
            </nav>
          )}
        </div>
      </header>

      <main className="w-full px-4 py-8">{children}</main>
    </div>
  );
}
