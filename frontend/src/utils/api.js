import axios from 'axios'

const API_URL = '/api'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => Promise.reject(error))

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (username, password) => api.post('/login', { username, password }),
  register: (username, email, password) => api.post('/register', { username, email, password }),
}

export const carsAPI = {
  getCars: (page = 1, pageSize = 20, filters = {}) => {
    const params = { page, page_size: pageSize }
    Object.keys(filters).forEach(key => {
      if (filters[key] !== '' && filters[key] !== null && filters[key] !== undefined) {
        params[key] = filters[key]
      }
    })
    return api.get('/cars', { params })
  },
  getCar: (id) => api.get(`/cars/${id}`),
  createCar: (car) => api.post('/cars', car),
  updateCar: (id, car) => api.put(`/cars/${id}`, car),
  deleteCar: (id) => api.delete(`/cars/${id}`),
}
