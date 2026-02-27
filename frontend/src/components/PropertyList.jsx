import PropertyCard from "./PropertyCard";

export default function PropertyList({ listings, favorites, onToggleFavorite, onSelect }) {
  if (listings.length === 0) {
    return (
      <div className="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="48" height="48">
          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
        <h3>No listings match your filters</h3>
        <p>Try adjusting your search criteria or clearing some filters.</p>
      </div>
    );
  }

  return (
    <div className="property-grid">
      {listings.map((listing) => (
        <PropertyCard
          key={listing.id}
          listing={listing}
          isFavorite={favorites.has(listing.id)}
          onToggleFavorite={onToggleFavorite}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
