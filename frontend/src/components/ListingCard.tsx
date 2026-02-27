import { Link } from "react-router-dom";
import type { Listing } from "../types/listing";

interface Props {
  listing: Listing;
}

function ListingCard({ listing }: Props) {
  const price =
    listing.price_per_month != null
      ? `$${listing.price_per_month}/mo`
      : listing.price_per_night != null
        ? `$${listing.price_per_night}/night`
        : "Price N/A";

  return (
    <Link
      to={`/listing/${listing.id}`}
      className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-4 block"
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-lg leading-tight">
          {listing.title_translated || listing.title}
        </h3>
        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded whitespace-nowrap ml-2">
          {listing.platform_name}
        </span>
      </div>

      <p className="text-gray-500 text-sm mb-3">
        {listing.city}, {listing.country}
        {listing.property_type && ` · ${listing.property_type}`}
        {listing.bedrooms && ` · ${listing.bedrooms} bed`}
      </p>

      <div className="flex justify-between items-center">
        <span className="text-indigo-600 font-bold">{price}</span>
        <div className="text-sm text-gray-500">
          {listing.rating && (
            <span>
              {listing.rating} ({listing.review_count})
            </span>
          )}
          {listing.aggregate_host_rating && (
            <span className="ml-2 text-green-600">
              Host: {listing.aggregate_host_rating}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}

export default ListingCard;
