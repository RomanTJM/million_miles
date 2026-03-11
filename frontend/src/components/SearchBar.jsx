const SearchBar = ({ value, onChange, onSubmit }) => {
  return (
    <div className="search-bar">
      <form className="search-bar-inner" onSubmit={onSubmit}>
        <input
          type="text"
          placeholder="Поиск по марке (Toyota, Nissan, Honda...)"
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
        <button type="submit" className="search-bar-btn">Найти</button>
      </form>
    </div>
  )
}

export default SearchBar
