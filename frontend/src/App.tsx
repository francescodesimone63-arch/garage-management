import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { message } from 'antd'
import { AuthProvider } from './contexts/AuthContext'
import PrivateRoute from './components/PrivateRoute'
import MainLayout from './layouts/MainLayout'
import LoginPage from './pages/auth/LoginPage'
import { OAuthCallback } from './pages/OAuthCallback'
import DashboardPage from './pages/dashboard/DashboardPage'
import CustomersPage from './pages/customers/CustomersPage'
import VehiclesPage from './pages/vehicles/VehiclesPage'
import WorkOrdersPage from './pages/work-orders/WorkOrdersPage'
import CMMWorkOrdersPage from './pages/cmm/CMMWorkOrdersPage'
import PartsPage from './pages/parts/PartsPage'
import TiresPage from './pages/tires/TiresPage'
import CourtesyCarsPage from './pages/courtesy-cars/CourtesyCarsPage'
import MaintenanceSchedulesPage from './pages/maintenance/MaintenanceSchedulesPage'
import CalendarPage from './pages/calendar/CalendarPage'
import NotificationsPage from './pages/notifications/NotificationsPage'
import UsersPage from './pages/users/UsersPage'
import ProfilePage from './pages/profile/ProfilePage'
import SettingsPage from './pages/settings/SettingsPage'
import NotFoundPage from './pages/NotFoundPage'

function App() {
  // Configura message globale
  useEffect(() => {
    message.config({
      top: 100,
      duration: 3,
      maxCount: 3,
    })
  }, [])

  return (
    <AuthProvider>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/oauth/callback" element={<OAuthCallback />} />

        {/* Protected routes */}
        <Route element={<PrivateRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/customers" element={<CustomersPage />} />
            <Route path="/vehicles" element={<VehiclesPage />} />
            <Route path="/work-orders" element={<WorkOrdersPage />} />
            <Route path="/cmm/work-orders" element={<CMMWorkOrdersPage />} />
            <Route path="/parts" element={<PartsPage />} />
            <Route path="/tires" element={<TiresPage />} />
            <Route path="/courtesy-cars" element={<CourtesyCarsPage />} />
            <Route path="/maintenance" element={<MaintenanceSchedulesPage />} />
            <Route path="/calendar" element={<CalendarPage />} />
            <Route path="/notifications" element={<NotificationsPage />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AuthProvider>
  )
}

export default App
