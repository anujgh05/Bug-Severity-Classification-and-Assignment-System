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
  const [username, setUsernameState] = useState(() => localStorage.getItem('username') || '');
  const [userId, setUserIdState] = useState(() => localStorage.getItem('userId'));

  const setRole = (nextRole, devId = null, uname = '', uid = null) => {
    setRoleState(nextRole);
    if (nextRole) {
      localStorage.setItem('role', nextRole);
    } else {
      localStorage.removeItem('role');
    }

    if (uname) {
      setUsernameState(uname);
      localStorage.setItem('username', uname);
    } else {
      setUsernameState('');
      localStorage.removeItem('username');
    }

    if (nextRole === 'developer' && devId) {
      setDeveloperIdState(String(devId));
      localStorage.setItem('developerId', String(devId));
    } else {
      setDeveloperIdState(null);
      localStorage.removeItem('developerId');
    }

    if (nextRole === 'user' && uid) {
      setUserIdState(String(uid));
      localStorage.setItem('userId', String(uid));
    } else if (nextRole !== 'user') {
      setUserIdState(null);
      localStorage.removeItem('userId');
    }
  };

  const loginSession = (userData) => {
    const { role: nextRole, developer_id: devId, username: uname, user_id: uid } = userData;
    setRole(nextRole, devId, uname, uid);
  };

  const logout = () => {
    setRoleState(null);
    setDeveloperIdState(null);
    setUserIdState(null);
    setUsernameState('');
    localStorage.removeItem('role');
    localStorage.removeItem('developerId');
    localStorage.removeItem('username');
    localStorage.removeItem('userId');
  };

  const value = useMemo(
    () => ({
      role,
      developerId,
      userId,
      username,
      setRole,
      loginSession,
      logout,
      isAuthenticated: Boolean(role),
      roles: ROLES,
    }),
    [role, developerId, username, userId],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export { ROLES };
