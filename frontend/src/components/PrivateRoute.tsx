import { Navigate, Outlet } from 'react-router-dom'
import { Spin } from 'antd'
import { useAuth } from '@/contexts/AuthContext'

const PrivateRoute = () => {
  const { user, loading } = useAuth()

  if (loading) {
    return <Spin fullscreen size="large" tip="Caricamento..." />
  }

  return user ? <Outlet /> : <Navigate to="/login" replace />
}

export default PrivateRoute
