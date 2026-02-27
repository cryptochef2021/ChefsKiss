import { sources, propertyTypes } from "../data/listings";

const PRICE_RANGES = [
  { label: "Any Price", min: 0, max: Infinity },
  { label: "Under $1,500", min: 0, max: 1500 },
  { label: "$1,500 – $2,000", min: 1500, max: 2000 },
  { label: "$2,000 – $3,000", min: 2000, max: 3000 },
  { label: "$3,000+", min: 3000, max: Infinity },
];

const BED_OPTIONS = [
  { label: "Any", value: -1 },
  { label: "Studio", value: 0 },
  { label: "1+", value: 1 },
  { label: "2+", value: 2 },
  { label: "3+", value: 3 },
];

export default function Filters({ filters, onFilterChange, resultCount }) {
  const handleChange = (key, value) => {
    onFilterChange({ ...filters, [key]: value });
  };

  return (
    <div className="filters">
      <div className="filters-row">
        <div className="filter-group">
          <label className="filter-label">Price</label>
          <select
            className="filter-select"
            value={filters.priceRange}
            onChange={(e) => handleChange("priceRange", Number(e.target.value))}
          >
            {PRICE_RANGES.map((range, i) => (
              <option key={i} value={i}>{range.label}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Beds</label>
          <div className="filter-chips">
            {BED_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                className={`filter-chip ${filters.beds === opt.value ? "active" : ""}`}
                onClick={() => handleChange("beds", opt.value)}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="filter-group">
          <label className="filter-label">Type</label>
          <select
            className="filter-select"
            value={filters.type}
            onChange={(e) => handleChange("type", e.target.value)}
          >
            <option value="All">All Types</option>
            {propertyTypes.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Source</label>
          <select
            className="filter-select"
            value={filters.source}
            onChange={(e) => handleChange("source", e.target.value)}
          >
            <option value="All">All Sources</option>
            {sources.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Pets</label>
          <button
            className={`filter-chip ${filters.petsOnly ? "active" : ""}`}
            onClick={() => handleChange("petsOnly", !filters.petsOnly)}
          >
            🐾 Pet-Friendly
          </button>
        </div>

        <div className="filter-group">
          <label className="filter-label">Sort</label>
          <select
            className="filter-select"
            value={filters.sort}
            onChange={(e) => handleChange("sort", e.target.value)}
          >
            <option value="price-asc">Price: Low → High</option>
            <option value="price-desc">Price: High → Low</option>
            <option value="sqft-desc">Size: Largest</option>
            <option value="newest">Newest Available</option>
          </select>
        </div>
      </div>

      <div className="filters-summary">
        <span className="result-count">{resultCount} listing{resultCount !== 1 ? "s" : ""} found</span>
      </div>
    </div>
  );
}

export { PRICE_RANGES };
