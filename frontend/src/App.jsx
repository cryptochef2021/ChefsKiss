import { useState, useCallback } from "react";
import Header from "./components/Header";
import SearchBar from "./components/SearchBar";
import Filters from "./components/Filters";
import PropertyList from "./components/PropertyList";
import PropertyDetail from "./components/PropertyDetail";
import useListings, { DEFAULT_FILTERS } from "./hooks/useListings";
import "./App.css";

export default function App() {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [favorites, setFavorites] = useState(new Set());
  const [showFavorites, setShowFavorites] = useState(false);
  const [selectedListing, setSelectedListing] = useState(null);

  const results = useListings(query, filters, favorites, showFavorites);

  const toggleFavorite = useCallback((id) => {
    setFavorites((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const toggleShowFavorites = useCallback(() => {
    setShowFavorites((prev) => !prev);
  }, []);

  return (
    <div className="app">
      <Header
        favoritesCount={favorites.size}
        onToggleFavorites={toggleShowFavorites}
        showFavorites={showFavorites}
      />
      <main className="main">
        <SearchBar query={query} onQueryChange={setQuery} />
        <Filters filters={filters} onFilterChange={setFilters} resultCount={results.length} />
        <PropertyList
          listings={results}
          favorites={favorites}
          onToggleFavorite={toggleFavorite}
          onSelect={setSelectedListing}
        />
      </main>
      <PropertyDetail
        listing={selectedListing}
        isFavorite={selectedListing ? favorites.has(selectedListing.id) : false}
        onToggleFavorite={toggleFavorite}
        onClose={() => setSelectedListing(null)}
      />
    </div>
  );
}
