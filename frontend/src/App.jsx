import { useState, useCallback, useRef, useEffect } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import FilterPanel from "./components/FilterPanel";
import ListingCard from "./components/ListingCard";
import ListingModal from "./components/ListingModal";
import ExportPanel from "./components/ExportPanel";
import ScrapeStatus from "./components/ScrapeStatus";
import StatsBar from "./components/StatsBar";
import { useListings } from "./hooks/useListings";

const queryClient = new QueryClient();

function Dashboard() {
  const [filters, setFilters] = useState({});
  const [selectedId, setSelectedId] = useState(null);
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading } = useListings(filters);

  const observerRef = useRef(null);
  const lastCardRef = useCallback(
    (node) => {
      if (isFetchingNextPage) return;
      if (observerRef.current) observerRef.current.disconnect();
      observerRef.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && hasNextPage) {
          fetchNextPage();
        }
      });
      if (node) observerRef.current.observe(node);
    },
    [isFetchingNextPage, fetchNextPage, hasNextPage]
  );

  const allItems = data?.pages.flatMap((p) => p.items) || [];
  const total = data?.pages[0]?.total || 0;

  return (
    <div className="min-h-screen bg-bg">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold">
            <span className="text-amber">Otodom</span> Scraper
          </h1>
          <ScrapeStatus />
        </div>
      </header>

      {/* Stats bar */}
      <div className="border-b border-gray-800 px-6 py-3">
        <div className="max-w-7xl mx-auto">
          <StatsBar />
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-7xl mx-auto px-6 py-6 flex gap-6">
        <FilterPanel filters={filters} setFilters={setFilters} />

        <main className="flex-1 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">{total} ogłoszeń</span>
            <ExportPanel filters={filters} />
          </div>

          {isLoading ? (
            <div className="text-center py-20 text-gray-400">Ładowanie ogłoszeń...</div>
          ) : allItems.length === 0 ? (
            <div className="text-center py-20 text-gray-400">Brak ogłoszeń pasujących do filtrów</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {allItems.map((item, idx) => {
                const isLast = idx === allItems.length - 1;
                return (
                  <div key={item.id} ref={isLast ? lastCardRef : undefined}>
                    <ListingCard listing={item} onClick={setSelectedId} />
                  </div>
                );
              })}
            </div>
          )}

          {isFetchingNextPage && (
            <div className="text-center py-4 text-gray-400">Ładowanie kolejnych...</div>
          )}
        </main>
      </div>

      {/* Modal */}
      {selectedId && (
        <ListingModal listingId={selectedId} onClose={() => setSelectedId(null)} />
      )}
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
}

export default App;
