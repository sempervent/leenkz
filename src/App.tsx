import React, { Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { AuthProvider } from '@/contexts/auth-context'
import { ProtectedRoute } from '@/components/auth/protected-route'

// Lazy load pages
const LandingPage = React.lazy(() => import('@/pages/landing'))
const LoginPage = React.lazy(() => import('@/pages/login'))
const RegisterPage = React.lazy(() => import('@/pages/register'))
const DashboardPage = React.lazy(() => import('@/pages/dashboard'))
const AdminPage = React.lazy(() => import('@/pages/admin'))
const SnapshotViewerPage = React.lazy(() => import('@/pages/snapshot-viewer'))

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-background">
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute requireAdmin>
                  <AdminPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/snapshots/:id"
              element={
                <ProtectedRoute>
                  <SnapshotViewerPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Suspense>
        <Toaster />
      </div>
    </AuthProvider>
  )
}

export default App 