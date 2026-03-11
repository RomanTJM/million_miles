import { Navigate } from 'react-router-dom'
import useAuthStore from '../stores/authStore'

const ProtectedRoute = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.token !== null)

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default ProtectedRoute
