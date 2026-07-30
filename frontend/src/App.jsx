import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import LoginPage from './pages/LoginPage.jsx';
import UserLoginPage from './pages/UserLoginPage.jsx';
import AdminLoginPage from './pages/AdminLoginPage.jsx';
import DeveloperLoginPage from './pages/DeveloperLoginPage.jsx';
import SubmitBugPage from './pages/SubmitBugPage.jsx';
import AdminTriagePage from './pages/AdminTriagePage.jsx';
import DeveloperTasksPage from './pages/DeveloperTasksPage.jsx';
import UserBugsPage from './pages/UserBugsPage.jsx';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/login/user" element={<UserLoginPage />} />
        <Route path="/login/admin" element={<AdminLoginPage />} />
        <Route path="/login/developer" element={<DeveloperLoginPage />} />
        <Route
          path="/submit-bug"
          element={
            <ProtectedRoute allowedRoles={['user']}>
              <SubmitBugPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/user/my-bugs"
          element={
            <ProtectedRoute allowedRoles={['user']}>
              <UserBugsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/triage"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminTriagePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/developer/my-tasks"
          element={
            <ProtectedRoute allowedRoles={['developer']}>
              <DeveloperTasksPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
