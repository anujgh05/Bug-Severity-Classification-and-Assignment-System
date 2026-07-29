import { createContext, useContext, useMemo, useState } from 'react';

const AuthContext = createContext(null);

const ROLES = {
  user: { label: 'End User', defaultPath: '/submit-bug' },
  admin: { label: 'Admin', defaultPath: '/admin/triage' },
  developer: { label: 'Developer', defaultPath: '/developer/my-tasks' },
};

export function AuthProvider({ children }) {
  const [role, setRoleState] = useState(() => localStorage.getItem('role'));
  const [developerId, setDeveloperIdState] = useState(() =>
    localStorage.getItem('developerId'),
  );

  const setRole = (nextRole, devId = null) => {
    setRoleState(nextRole);
    localStorage.setItem('role', nextRole);
    if (nextRole === 'developer' && devId) {
      setDeveloperIdState(String(devId));
      localStorage.setItem('developerId', String(devId));
    } else {
      setDeveloperIdState(null);
      localStorage.removeItem('developerId');
    }
  };

  const logout = () => {
    setRoleState(null);
    setDeveloperIdState(null);
    localStorage.removeItem('role');
    localStorage.removeItem('developerId');
  };

  const value = useMemo(
    () => ({
      role,
      developerId,
      setRole,
      logout,
      isAuthenticated: Boolean(role),
      roles: ROLES,
    }),
    [role, developerId],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export { ROLES };
