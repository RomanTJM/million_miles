import { useState, useEffect } from 'react'
import { carsAPI } from '../utils/api'
import useCarsStore from '../stores/carsStore'
import Header from '../components/Header'
import SearchBar from '../components/SearchBar'
import Sidebar from '../components/Sidebar'
import '../styles/Home.css'

const Home = () => {
  const cars = useCarsStore((state) => state.cars)
  const setCars = useCarsStore((state) => state.setCars)
  const total = useCarsStore((state) => state.total)
  const setTotal = useCarsStore((state) => state.setTotal)
  const page = useCarsStore((state) => state.page)
  const setPage = useCarsStore((state) => state.setPage)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [filters, setFilters] = useState({
    brand: '',
    model: '',
    year_from: '',
    year_to: '',
    price_from: '',
    price_to: '',
  })

  const pageSize = 20

  useEffect(() => {
    fetchCars()
  }, [page, filters])

  const fetchCars = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await carsAPI.getCars(page, pageSize, filters)
      setCars(response.data.items)
      setTotal(response.data.total)
    } catch (err) {
      setError('Ошибка при загрузке данных')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (e) => {
    const { name, value } = e.target
    setFilters((prev) => ({
      ...prev,
      [name]: value === '' ? '' : name.includes('price') || name.includes('year') ? parseInt(value) : value,
    }))
    setPage(1)
  }

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    setFilters((prev) => ({ ...prev, brand: searchInput }))
    setPage(1)
  }

  const handleReset = () => {
    setFilters({ brand: '', model: '', year_from: '', year_to: '', price_from: '', price_to: '' })
    setSearchInput('')
    setPage(1)
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
    }).format(price)
  }

  const totalPages = Math.ceil(total / pageSize)

  const renderPagination = () => {
    if (totalPages <= 1) return null
    const pages = []
    const delta = 2
    for (let i = Math.max(1, page - delta); i <= Math.min(totalPages, page + delta); i++) {
      pages.push(i)
    }
    return (
      <div className="pagination">
        <button onClick={() => setPage(1)} disabled={page === 1}>«</button>
        <button onClick={() => setPage(page - 1)} disabled={page === 1}>‹ Назад</button>
        {pages[0] > 1 && <span className="page-info">...</span>}
        {pages.map((p) => (
          <button
            key={p}
            onClick={() => setPage(p)}
            style={p === page ? { background: 'var(--cs-red)', borderColor: 'var(--cs-red)', color: 'white' } : {}}
          >
            {p}
          </button>
        ))}
        {pages[pages.length - 1] < totalPages && <span className="page-info">...</span>}
        <button onClick={() => setPage(page + 1)} disabled={page === totalPages}>Вперёд ›</button>
        <button onClick={() => setPage(totalPages)} disabled={page === totalPages}>»</button>
        <span className="page-info">{page} / {totalPages}</span>
      </div>
    )
  }

  return (
    <div className="home-container">
      <Header />

      <SearchBar
        value={searchInput}
        onChange={setSearchInput}
        onSubmit={handleSearchSubmit}
      />

      <div className="page-layout">
        <Sidebar
          filters={filters}
          onChange={handleFilterChange}
          onReset={handleReset}
        />

        <main className="main-list">
          {error && <div className="error-message">{error}</div>}

          <div className="results-header">
            <div className="results-count">
              <strong>{total}</strong> объявлений найдено
            </div>
          </div>

          {loading ? (
            <div className="loading">Загрузка...</div>
          ) : cars.length === 0 ? (
            <div className="no-cars">Объявлений не найдено</div>
          ) : (
            <>
              <div className="cars-list">
                {cars.map((car) => (
                  <div key={car.id} className="car-card">
                    <div className="car-image">
                      <div className="car-image-icon">🚗</div>
                      <div className="car-image-label">Нет фото</div>
                    </div>

                    <div className="car-body">
                      <div className="car-brand">{car.brand}</div>
                      <div className="car-name">{car.brand} {car.model}</div>

                      <div className="car-specs">
                        <div className="spec-row">
                          <span className="spec-label">Год:</span>
                          <span className="spec-value">{car.year}</span>
                        </div>
                        <div className="spec-row">
                          <span className="spec-label">Цвет:</span>
                          <span className="spec-value">
                            {car.color && car.color !== 'Unknown' ? car.color : 'Не указан'}
                          </span>
                        </div>
                      </div>

                      <div className="car-price-block">
                        <div className="price-row">
                          <span className="price-label">Цена</span>
                          <span className="price-total">{formatPrice(car.price)}</span>
                        </div>
                        <a
                          href={car.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="view-btn"
                        >
                          Смотреть объявление
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {renderPagination()}
            </>
          )}
        </main>
      </div>
    </div>
  )
}

export default Home
