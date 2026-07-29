import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

export default function ProtectedRoute({ allowedRoles, children }) {
  const { role, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(role)) {
    const fallback = role === 'admin' ? '/admin/triage' : role === 'developer' ? '/developer/my-tasks' : '/submit-bug';
    return <Navigate to={fallback} replace />;
  }

  return children;
}
