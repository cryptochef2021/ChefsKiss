export default function SearchBar({ query, onQueryChange }) {
  return (
    <div className="search-bar">
      <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
      <input
        type="text"
        className="search-input"
        placeholder="Search by address, neighborhood, or keyword..."
        value={query}
        onChange={(e) => onQueryChange(e.target.value)}
      />
      {query && (
        <button className="search-clear" onClick={() => onQueryChange("")}>
          &times;
        </button>
      )}
    </div>
  );
}
