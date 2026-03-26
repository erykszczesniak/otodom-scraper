import { useState } from "react";
import { exportUrl } from "../api";

export default function ExportPanel({ filters }) {
  const [copied, setCopied] = useState(false);

  const handleExport = (format) => {
    window.open(exportUrl(filters, format), "_blank");
  };

  const handleCopyJson = async () => {
    try {
      const resp = await fetch(exportUrl(filters, "json"));
      const data = await resp.json();
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore
    }
  };

  return (
    <div className="flex items-center gap-3 text-sm">
      <span className="text-gray-400">Eksportuj:</span>
      <button onClick={() => handleExport("json")} className="text-amber hover:underline">JSON</button>
      <button onClick={() => handleExport("xml")} className="text-amber hover:underline">XML</button>
      <button onClick={() => handleExport("csv")} className="text-amber hover:underline">CSV</button>
      <button onClick={handleCopyJson} className="text-gray-400 hover:text-white transition">
        {copied ? "Skopiowano!" : "Kopiuj JSON"}
      </button>
    </div>
  );
}
