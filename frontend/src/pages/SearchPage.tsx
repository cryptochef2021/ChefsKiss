import { useState } from "react";
import type { Listing, SearchParams } from "../types/listing";
import { searchListings } from "../services/api";
import ListingCard from "../components/ListingCard";
import SearchBar from "../components/SearchBar";

function SearchPage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (params: SearchParams) => {
    setLoading(true);
    try {
      const results = await searchListings(params);
      setListings(results);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <SearchBar onSearch={handleSearch} />

      {loading && (
        <div className="text-center py-12 text-gray-500">
          Searching across platforms...
        </div>
      )}

      {!loading && listings.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          Search for a city to see aggregated rental listings
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
        {listings.map((listing) => (
          <ListingCard key={listing.id} listing={listing} />
        ))}
      </div>
    </div>
  );
}

export default SearchPage;
