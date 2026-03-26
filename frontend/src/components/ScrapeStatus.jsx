import { useState } from "react";
import { useScrapeStatus } from "../hooks/useListings";
import { triggerScrape } from "../api";

function timeAgo(dateStr) {
  if (!dateStr) return "nigdy";
  const diff = Date.now() - new Date(dateStr).getTime();
  const min = Math.round(diff / 60000);
  if (min < 1) return "przed chwilą";
  if (min < 60) return `${min} min temu`;
  const hours = Math.round(min / 60);
  if (hours < 24) return `${hours}h temu`;
  return `${Math.round(hours / 24)}d temu`;
}

export default function ScrapeStatus() {
  const { data: runs } = useScrapeStatus();
  const [scraping, setScraping] = useState(false);

  const lastRun = runs?.[0];
  const isRunning = lastRun && !lastRun.finished_at;

  const handleScrape = async () => {
    setScraping(true);
    try {
      await triggerScrape();
    } finally {
      setTimeout(() => setScraping(false), 3000);
    }
  };

  return (
    <div className="flex items-center gap-3 text-sm">
      <span className="text-gray-500">
        Ostatni scrape: {lastRun ? timeAgo(lastRun.finished_at || lastRun.started_at) : "nigdy"}
      </span>
      {lastRun && (
        <span className="text-gray-600">
          ({lastRun.listings_new} nowych, {lastRun.listings_updated} zaktualizowanych)
        </span>
      )}
      <button
        onClick={handleScrape}
        disabled={scraping || isRunning}
        className="text-amber hover:underline disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {scraping || isRunning ? "Scrapowanie..." : "Odśwież teraz"}
      </button>
    </div>
  );
}
