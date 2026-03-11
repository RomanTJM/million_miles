const Sidebar = ({ filters, onChange, onReset }) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <div className="sidebar-title">Фильтры</div>
        <div className="sidebar-fields">
          <div className="sidebar-field">
            <label>Марка</label>
            <input
              type="text"
              name="brand"
              value={filters.brand}
              onChange={onChange}
              placeholder="Любая"
            />
          </div>
          <div className="sidebar-field">
            <label>Модель</label>
            <input
              type="text"
              name="model"
              value={filters.model}
              onChange={onChange}
              placeholder="Любая"
            />
          </div>
          <div className="sidebar-field">
            <label>Год</label>
            <div className="sidebar-range">
              <input
                type="number"
                name="year_from"
                value={filters.year_from}
                onChange={onChange}
                placeholder="От"
              />
              <span>—</span>
              <input
                type="number"
                name="year_to"
                value={filters.year_to}
                onChange={onChange}
                placeholder="До"
              />
            </div>
          </div>
          <div className="sidebar-field">
            <label>Цена (₽)</label>
            <div className="sidebar-range">
              <input
                type="number"
                name="price_from"
                value={filters.price_from}
                onChange={onChange}
                placeholder="От"
              />
              <span>—</span>
              <input
                type="number"
                name="price_to"
                value={filters.price_to}
                onChange={onChange}
                placeholder="До"
              />
            </div>
          </div>
          <button onClick={onReset} className="btn-reset">Сбросить</button>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
