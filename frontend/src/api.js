const API_BASE = "/api";

export async function fetchListings(filters = {}, page = 1) {
  const params = new URLSearchParams();
  params.set("page", page);
  params.set("per_page", "50");
  params.set("format", "json");

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      if (Array.isArray(value)) {
        value.forEach((v) => params.append(key, v));
      } else {
        params.set(key, value);
      }
    }
  });

  const resp = await fetch(`${API_BASE}/listings?${params}`);
  if (!resp.ok) throw new Error("Failed to fetch listings");
  return resp.json();
}

export async function fetchListing(id) {
  const resp = await fetch(`${API_BASE}/listings/${id}`);
  if (!resp.ok) throw new Error("Failed to fetch listing");
  return resp.json();
}

export async function fetchPriceHistory(id) {
  const resp = await fetch(`${API_BASE}/listings/${id}/price-history`);
  if (!resp.ok) throw new Error("Failed to fetch price history");
  return resp.json();
}

export async function fetchStats() {
  const resp = await fetch(`${API_BASE}/listings/stats/overview`);
  if (!resp.ok) throw new Error("Failed to fetch stats");
  return resp.json();
}

export async function fetchScrapeStatus() {
  const resp = await fetch(`${API_BASE}/scrape/status`);
  if (!resp.ok) throw new Error("Failed to fetch scrape status");
  return resp.json();
}

export async function triggerScrape() {
  const resp = await fetch(`${API_BASE}/scrape`, { method: "POST" });
  if (!resp.ok) throw new Error("Failed to trigger scrape");
  return resp.json();
}

export function exportUrl(filters, format) {
  const params = new URLSearchParams();
  params.set("format", format);
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      if (Array.isArray(value)) {
        value.forEach((v) => params.append(key, v));
      } else {
        params.set(key, value);
      }
    }
  });
  return `${API_BASE}/listings?${params}`;
}
