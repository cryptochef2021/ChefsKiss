import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import type { Listing } from "../types/listing";
import { getListing, compareListingPrices } from "../services/api";

interface PriceComparison {
  platform: string;
  price_per_night: number | null;
  price_per_month: number | null;
  currency: string;
  url: string;
}

function ListingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [listing, setListing] = useState<Listing | null>(null);
  const [comparisons, setComparisons] = useState<PriceComparison[]>([]);

  useEffect(() => {
    if (!id) return;
    const listingId = parseInt(id, 10);
    getListing(listingId).then(setListing);
    compareListingPrices(listingId).then((data) =>
      setComparisons(data.comparisons)
    );
  }, [id]);

  if (!listing) {
    return <div className="text-center py-12">Loading...</div>;
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold mb-2">
        {listing.title_translated || listing.title}
      </h2>
      <p className="text-gray-500 mb-4">
        {listing.city}, {listing.country} &middot; via {listing.platform_name}
      </p>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Nightly:</span>{" "}
            {listing.price_per_night
              ? `${listing.currency} ${listing.price_per_night}`
              : "N/A"}
          </div>
          <div>
            <span className="text-gray-500">Monthly:</span>{" "}
            {listing.price_per_month
              ? `${listing.currency} ${listing.price_per_month}`
              : "N/A"}
          </div>
          <div>
            <span className="text-gray-500">Type:</span>{" "}
            {listing.property_type || "N/A"}
          </div>
          <div>
            <span className="text-gray-500">Bedrooms:</span>{" "}
            {listing.bedrooms ?? "N/A"}
          </div>
          <div>
            <span className="text-gray-500">Rating:</span>{" "}
            {listing.rating ?? "N/A"} ({listing.review_count} reviews)
          </div>
          <div>
            <span className="text-gray-500">Host rating:</span>{" "}
            {listing.aggregate_host_rating ?? "N/A"} (
            {listing.total_host_reviews} across all platforms)
          </div>
        </div>
      </div>

      {comparisons.length > 1 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-3">Price Comparison</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Platform</th>
                <th className="pb-2">Nightly</th>
                <th className="pb-2">Monthly</th>
                <th className="pb-2"></th>
              </tr>
            </thead>
            <tbody>
              {comparisons.map((c, i) => (
                <tr key={i} className="border-b last:border-0">
                  <td className="py-2">{c.platform}</td>
                  <td className="py-2">
                    {c.price_per_night
                      ? `${c.currency} ${c.price_per_night}`
                      : "-"}
                  </td>
                  <td className="py-2">
                    {c.price_per_month
                      ? `${c.currency} ${c.price_per_month}`
                      : "-"}
                  </td>
                  <td className="py-2">
                    <a
                      href={c.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-indigo-600 hover:underline"
                    >
                      View
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default ListingDetailPage;
