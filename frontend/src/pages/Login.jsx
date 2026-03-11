import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI } from '../utils/api'
import useAuthStore from '../stores/authStore'
import '../styles/Login.css'

const Login = () => {
  const navigate = useNavigate()
  const setToken = useAuthStore((state) => state.setToken)
  const setUser = useAuthStore((state) => state.setUser)
  
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showRegister, setShowRegister] = useState(false)
  const [email, setEmail] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      const response = await authAPI.login(username, password)
      setToken(response.data.access_token)
      setUser(response.data.user)
      navigate('/')
    } catch (err) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(', '))
      } else {
        setError(detail || 'Ошибка при входе')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      await authAPI.register(username, email, password)
      setError('')
      setShowRegister(false)
      setUsername('')
      setEmail('')
      setPassword('')
      setError('success: Регистрация успешна! Теперь войдите в систему')
    } catch (err) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(', '))
      } else {
        setError(detail || 'Ошибка при регистрации')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-card-header">
          <div className="login-logo-icon">🚗</div>
          <div>
            <span className="login-logo-text">MillionMiles</span>
            <span className="login-logo-sub">Авторынок</span>
          </div>
        </div>

        <div className="login-card-body">
          <h2>{showRegister ? 'Регистрация' : 'Вход в систему'}</h2>

          {error && (
            <div className={`error-message ${error.includes('success') ? 'success' : ''}`}>
              {error.replace('success: ', '')}
            </div>
          )}

          <form onSubmit={showRegister ? handleRegister : handleLogin}>
            <div className="form-group">
              <label>Имя пользователя</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
                placeholder="Введите имя пользователя"
              />
            </div>

            {showRegister && (
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="Введите email"
                />
              </div>
            )}

            <div className="form-group">
              <label>Пароль</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete={showRegister ? 'new-password' : 'current-password'}
                placeholder="Введите пароль"
              />
            </div>

            {!showRegister && password.length === 0 && (
              <small>По умолчанию: admin / admin123</small>
            )}

            <button type="submit" disabled={loading}>
              {loading ? 'Загрузка...' : (showRegister ? 'Зарегистрироваться' : 'Войти')}
            </button>
          </form>

          <button
            className="toggle-button"
            onClick={() => {
              setShowRegister(!showRegister)
              setError('')
            }}
          >
            {showRegister ? 'Уже есть аккаунт? Войти' : 'Нет аккаунта? Зарегистрироваться'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Login
