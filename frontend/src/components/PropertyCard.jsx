const SOURCE_COLORS = {
  Zillow: "#006aff",
  "Apartments.com": "#e63946",
  Craigslist: "#5f2eea",
  "Realtor.com": "#d4380d",
};

export default function PropertyCard({ listing, isFavorite, onToggleFavorite, onSelect }) {
  const color = SOURCE_COLORS[listing.source] || "#666";

  return (
    <div className="property-card" onClick={() => onSelect(listing)}>
      <div className="card-image-wrapper">
        <img
          className="card-image"
          src={listing.image}
          alt={listing.title}
          loading="lazy"
        />
        <span className="card-source" style={{ backgroundColor: color }}>
          {listing.source}
        </span>
        <button
          className={`card-fav-btn ${isFavorite ? "active" : ""}`}
          onClick={(e) => {
            e.stopPropagation();
            onToggleFavorite(listing.id);
          }}
          title={isFavorite ? "Remove from saved" : "Save listing"}
        >
          <svg viewBox="0 0 24 24" fill={isFavorite ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" width="20" height="20">
            <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z" />
          </svg>
        </button>
      </div>
      <div className="card-body">
        <div className="card-price">${listing.price.toLocaleString()}<span className="card-price-period">/mo</span></div>
        <h3 className="card-title">{listing.title}</h3>
        <p className="card-address">{listing.address}, {listing.city}, {listing.state} {listing.zip}</p>
        <div className="card-details">
          <span>{listing.beds === 0 ? "Studio" : `${listing.beds} bd`}</span>
          <span className="card-dot">·</span>
          <span>{listing.baths} ba</span>
          <span className="card-dot">·</span>
          <span>{listing.sqft.toLocaleString()} sqft</span>
        </div>
        <div className="card-tags">
          {listing.pets && <span className="card-tag pet">Pet-Friendly</span>}
          <span className="card-tag type">{listing.type}</span>
        </div>
      </div>
    </div>
  );
}
