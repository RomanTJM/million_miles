import { useNavigate } from 'react-router-dom'
import useAuthStore from '../stores/authStore'

const Header = () => {
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)
  const user = useAuthStore((state) => state.user)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-logo">
          <div className="header-logo-icon">🚗</div>
          <div>
            <span className="header-logo-text">MillionMiles</span>
            <span className="header-logo-sub">Авторынок</span>
          </div>
        </div>
        <div className="user-section">
          <span className="user-name">{user?.username}</span>
          <button onClick={handleLogout} className="logout-btn">Выход</button>
        </div>
      </div>
    </header>
  )
}

export default Header
