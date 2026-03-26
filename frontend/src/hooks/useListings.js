import { useInfiniteQuery, useQuery } from "@tanstack/react-query";
import { fetchListings, fetchListing, fetchPriceHistory, fetchStats, fetchScrapeStatus } from "../api";

export function useListings(filters) {
  return useInfiniteQuery({
    queryKey: ["listings", filters],
    queryFn: ({ pageParam = 1 }) => fetchListings(filters, pageParam),
    getNextPageParam: (lastPage) => {
      if (lastPage.page < lastPage.pages) return lastPage.page + 1;
      return undefined;
    },
    staleTime: 60_000,
  });
}

export function useListing(id) {
  return useQuery({
    queryKey: ["listing", id],
    queryFn: () => fetchListing(id),
    enabled: !!id,
  });
}

export function usePriceHistory(id) {
  return useQuery({
    queryKey: ["priceHistory", id],
    queryFn: () => fetchPriceHistory(id),
    enabled: !!id,
  });
}

export function useStats() {
  return useQuery({
    queryKey: ["stats"],
    queryFn: fetchStats,
    staleTime: 60_000,
  });
}

export function useScrapeStatus() {
  return useQuery({
    queryKey: ["scrapeStatus"],
    queryFn: fetchScrapeStatus,
    refetchInterval: 10_000,
  });
}
