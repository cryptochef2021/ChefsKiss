import { useMemo } from "react";
import allListings from "../data/listings";
import { PRICE_RANGES } from "../components/Filters";

export const DEFAULT_FILTERS = {
  priceRange: 0,
  beds: -1,
  type: "All",
  source: "All",
  petsOnly: false,
  sort: "price-asc",
};

export default function useListings(query, filters, favorites, showFavorites) {
  return useMemo(() => {
    let results = [...allListings];

    // Show only favorites
    if (showFavorites) {
      results = results.filter((l) => favorites.has(l.id));
    }

    // Text search
    if (query.trim()) {
      const q = query.toLowerCase();
      results = results.filter(
        (l) =>
          l.title.toLowerCase().includes(q) ||
          l.address.toLowerCase().includes(q) ||
          l.city.toLowerCase().includes(q) ||
          l.description.toLowerCase().includes(q) ||
          l.type.toLowerCase().includes(q)
      );
    }

    // Price filter
    if (filters.priceRange !== 0) {
      const range = PRICE_RANGES[filters.priceRange];
      results = results.filter((l) => l.price >= range.min && l.price <= range.max);
    }

    // Beds filter
    if (filters.beds >= 0) {
      results = results.filter((l) => l.beds >= filters.beds);
    }

    // Type filter
    if (filters.type !== "All") {
      results = results.filter((l) => l.type === filters.type);
    }

    // Source filter
    if (filters.source !== "All") {
      results = results.filter((l) => l.source === filters.source);
    }

    // Pets filter
    if (filters.petsOnly) {
      results = results.filter((l) => l.pets);
    }

    // Sorting
    switch (filters.sort) {
      case "price-asc":
        results.sort((a, b) => a.price - b.price);
        break;
      case "price-desc":
        results.sort((a, b) => b.price - a.price);
        break;
      case "sqft-desc":
        results.sort((a, b) => b.sqft - a.sqft);
        break;
      case "newest":
        results.sort((a, b) => new Date(a.available) - new Date(b.available));
        break;
    }

    return results;
  }, [query, filters, favorites, showFavorites]);
}
