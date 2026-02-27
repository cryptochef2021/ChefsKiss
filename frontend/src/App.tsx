import { Routes, Route } from "react-router-dom";
import SearchPage from "./pages/SearchPage";
import ListingDetailPage from "./pages/ListingDetailPage";

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-indigo-600">StayAgg</h1>
          <p className="text-sm text-gray-500">
            Find the best rental deals across every platform
          </p>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/listing/:id" element={<ListingDetailPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
