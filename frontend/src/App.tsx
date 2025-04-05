import React, { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Layout
import MainLayout from './components/layout/MainLayout';

// Pages with eager loading
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// Pages with lazy loading
const Dashboard = lazy(() => import('./pages/Dashboard'));
const UploadPage = lazy(() => import('./pages/UploadPage'));
const TemplatesPage = lazy(() => import('./pages/TemplatesPage'));
const VideoCreationPage = lazy(() => import('./pages/VideoCreationPage'));
const BrandSettingsPage = lazy(() => import('./pages/BrandSettingsPage'));

// Loading fallback
const LoadingFallback = () => (
  <div className="flex justify-center items-center h-screen">
    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
  </div>
);

// Protected route component
interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <LoadingFallback />;
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      {/* Protected routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={
            <Suspense fallback={<LoadingFallback />}>
              <Dashboard />
            </Suspense>
          }
        />
        <Route
          path="upload"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <UploadPage />
            </Suspense>
          }
        />
        <Route
          path="templates"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <TemplatesPage />
            </Suspense>
          }
        />
        <Route
          path="video-creation/:contentId"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <VideoCreationPage />
            </Suspense>
          }
        />
        <Route
          path="brand-settings"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <BrandSettingsPage />
            </Suspense>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;
