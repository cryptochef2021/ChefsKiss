import { useState } from "react";
import type { SearchParams } from "../types/listing";

interface Props {
  onSearch: (params: SearchParams) => void;
}

function SearchBar({ onSearch }: Props) {
  const [city, setCity] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [priceType, setPriceType] = useState<"monthly" | "nightly">("monthly");
  const [sortBy, setSortBy] = useState<"price" | "rating" | "reviews">("price");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({
      city: city || undefined,
      max_price: maxPrice ? parseFloat(maxPrice) : undefined,
      price_type: priceType,
      sort_by: sortBy,
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white rounded-lg shadow p-4 flex flex-wrap gap-4 items-end"
    >
      <div className="flex-1 min-w-[200px]">
        <label className="block text-sm text-gray-600 mb-1">City</label>
        <input
          type="text"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          placeholder="Da Nang, Bangkok, Bali..."
          className="w-full border rounded px-3 py-2"
        />
      </div>

      <div className="w-32">
        <label className="block text-sm text-gray-600 mb-1">Max Price</label>
        <input
          type="number"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
          placeholder="USD"
          className="w-full border rounded px-3 py-2"
        />
      </div>

      <div className="w-32">
        <label className="block text-sm text-gray-600 mb-1">Price Type</label>
        <select
          value={priceType}
          onChange={(e) =>
            setPriceType(e.target.value as "monthly" | "nightly")
          }
          className="w-full border rounded px-3 py-2"
        >
          <option value="monthly">Monthly</option>
          <option value="nightly">Nightly</option>
        </select>
      </div>

      <div className="w-32">
        <label className="block text-sm text-gray-600 mb-1">Sort By</label>
        <select
          value={sortBy}
          onChange={(e) =>
            setSortBy(e.target.value as "price" | "rating" | "reviews")
          }
          className="w-full border rounded px-3 py-2"
        >
          <option value="price">Price</option>
          <option value="rating">Rating</option>
          <option value="reviews">Reviews</option>
        </select>
      </div>

      <button
        type="submit"
        className="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700"
      >
        Search
      </button>
    </form>
  );
}

export default SearchBar;
