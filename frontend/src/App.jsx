import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import LoginPage from './pages/LoginPage.jsx';
import SubmitBugPage from './pages/SubmitBugPage.jsx';
import AdminTriagePage from './pages/AdminTriagePage.jsx';
import DeveloperTasksPage from './pages/DeveloperTasksPage.jsx';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route
          path="/submit-bug"
          element={
            <ProtectedRoute allowedRoles={['user']}>
              <SubmitBugPage />
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
