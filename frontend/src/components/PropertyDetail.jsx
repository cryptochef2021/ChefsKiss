const SOURCE_COLORS = {
  Zillow: "#006aff",
  "Apartments.com": "#e63946",
  Craigslist: "#5f2eea",
  "Realtor.com": "#d4380d",
};

export default function PropertyDetail({ listing, isFavorite, onToggleFavorite, onClose }) {
  if (!listing) return null;
  const color = SOURCE_COLORS[listing.source] || "#666";

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>&times;</button>

        <div className="detail-image-wrapper">
          <img className="detail-image" src={listing.image} alt={listing.title} />
          <span className="card-source" style={{ backgroundColor: color }}>{listing.source}</span>
        </div>

        <div className="detail-body">
          <div className="detail-header">
            <div>
              <div className="detail-price">${listing.price.toLocaleString()}<span className="card-price-period">/mo</span></div>
              <h2 className="detail-title">{listing.title}</h2>
              <p className="detail-address">{listing.address}, {listing.city}, {listing.state} {listing.zip}</p>
            </div>
            <button
              className={`detail-fav-btn ${isFavorite ? "active" : ""}`}
              onClick={() => onToggleFavorite(listing.id)}
            >
              <svg viewBox="0 0 24 24" fill={isFavorite ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" width="22" height="22">
                <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z" />
              </svg>
              {isFavorite ? "Saved" : "Save"}
            </button>
          </div>

          <div className="detail-stats">
            <div className="detail-stat">
              <span className="stat-value">{listing.beds === 0 ? "Studio" : listing.beds}</span>
              <span className="stat-label">{listing.beds === 0 ? "" : "Beds"}</span>
            </div>
            <div className="detail-stat">
              <span className="stat-value">{listing.baths}</span>
              <span className="stat-label">Baths</span>
            </div>
            <div className="detail-stat">
              <span className="stat-value">{listing.sqft.toLocaleString()}</span>
              <span className="stat-label">Sq Ft</span>
            </div>
            <div className="detail-stat">
              <span className="stat-value">{listing.type}</span>
              <span className="stat-label">Type</span>
            </div>
          </div>

          <div className="detail-section">
            <h3>Description</h3>
            <p>{listing.description}</p>
          </div>

          <div className="detail-section">
            <h3>Details</h3>
            <div className="detail-info-grid">
              <div className="detail-info-item">
                <span className="info-label">Available</span>
                <span className="info-value">{new Date(listing.available).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}</span>
              </div>
              <div className="detail-info-item">
                <span className="info-label">Parking</span>
                <span className="info-value">{listing.parking}</span>
              </div>
              <div className="detail-info-item">
                <span className="info-label">Pets</span>
                <span className="info-value">{listing.pets ? "Allowed" : "Not Allowed"}</span>
              </div>
              <div className="detail-info-item">
                <span className="info-label">Source</span>
                <span className="info-value" style={{ color }}>{listing.source}</span>
              </div>
            </div>
          </div>

          <div className="detail-section">
            <h3>Amenities</h3>
            <div className="detail-amenities">
              {listing.amenities.map((a) => (
                <span key={a} className="amenity-tag">{a}</span>
              ))}
            </div>
          </div>

          <div className="detail-actions">
            <button className="btn-primary">Contact Landlord</button>
            <button className="btn-secondary">Schedule Tour</button>
          </div>
        </div>
      </div>
    </div>
  );
}
