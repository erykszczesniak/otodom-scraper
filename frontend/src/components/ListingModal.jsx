import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { useListing, usePriceHistory } from "../hooks/useListings";

export default function ListingModal({ listingId, onClose }) {
  const { data: listing, isLoading } = useListing(listingId);
  const { data: priceHistory } = usePriceHistory(listingId);
  const [imgIdx, setImgIdx] = useState(0);

  if (!listingId) return null;

  let images = [];
  try {
    images = listing?.images ? JSON.parse(listing.images) : [];
  } catch {
    images = [];
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4" onClick={onClose}>
      <div
        className="bg-card rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {isLoading ? (
          <div className="p-8 text-center text-gray-400">Ładowanie...</div>
        ) : listing ? (
          <>
            {/* Gallery */}
            {images.length > 0 && (
              <div className="relative">
                <img
                  src={images[imgIdx]}
                  alt={listing.title}
                  className="w-full h-72 object-cover rounded-t-2xl"
                />
                {images.length > 1 && (
                  <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1">
                    {images.slice(0, 10).map((_, i) => (
                      <button
                        key={i}
                        onClick={() => setImgIdx(i)}
                        className={`w-2 h-2 rounded-full ${i === imgIdx ? "bg-amber" : "bg-white/50"}`}
                      />
                    ))}
                  </div>
                )}
                <div className="absolute top-3 left-3 flex gap-2">
                  {imgIdx > 0 && (
                    <button onClick={() => setImgIdx(imgIdx - 1)} className="bg-black/50 text-white rounded-full w-8 h-8 flex items-center justify-center">‹</button>
                  )}
                  {imgIdx < images.length - 1 && (
                    <button onClick={() => setImgIdx(imgIdx + 1)} className="bg-black/50 text-white rounded-full w-8 h-8 flex items-center justify-center">›</button>
                  )}
                </div>
              </div>
            )}

            <div className="p-6 space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-bold">{listing.title}</h2>
                  {listing.address && <p className="text-sm text-gray-400">{listing.address}</p>}
                  {listing.district && <p className="text-xs text-gray-500">{listing.district}</p>}
                </div>
                <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl leading-none">&times;</button>
              </div>

              <div className="text-3xl font-bold text-amber">
                {listing.price ? `${listing.price.toLocaleString("pl-PL")} PLN/mies.` : "Cena nieznana"}
              </div>

              {listing.deposit > 0 && (
                <p className="text-sm text-gray-400">Kaucja: {listing.deposit.toLocaleString("pl-PL")} PLN</p>
              )}

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
                {listing.area && <div className="bg-bg rounded-lg p-3"><span className="text-gray-400">Metraż</span><br />{listing.area} m²</div>}
                {listing.rooms && <div className="bg-bg rounded-lg p-3"><span className="text-gray-400">Pokoje</span><br />{listing.rooms}</div>}
                {listing.floor != null && <div className="bg-bg rounded-lg p-3"><span className="text-gray-400">Piętro</span><br />{listing.floor}{listing.total_floors ? `/${listing.total_floors}` : ""}</div>}
                {listing.metro_distance_min != null && <div className="bg-bg rounded-lg p-3"><span className="text-gray-400">🚇 Metro</span><br />{listing.metro_distance_min} min</div>}
                {listing.center_distance_min != null && <div className="bg-bg rounded-lg p-3"><span className="text-gray-400">🏙️ Centrum</span><br />{listing.center_distance_min} min</div>}
                {listing.furnished && <div className="bg-bg rounded-lg p-3"><span className="text-gray-400">Umeblowane</span><br />{listing.furnished}</div>}
              </div>

              <div className="flex flex-wrap gap-2 text-xs">
                {listing.has_bathtub && <span className="bg-bg px-3 py-1 rounded-full">🛁 Wanna</span>}
                {listing.pets_allowed && <span className="bg-bg px-3 py-1 rounded-full">🐾 Zwierzęta</span>}
                {listing.has_balcony && <span className="bg-bg px-3 py-1 rounded-full">🌿 Balkon</span>}
                {listing.has_parking && <span className="bg-bg px-3 py-1 rounded-full">🅿️ Parking</span>}
                {listing.has_elevator && <span className="bg-bg px-3 py-1 rounded-full">🛗 Winda</span>}
                {!listing.agency_fee && <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full">Bez prowizji</span>}
              </div>

              {listing.description && (
                <div>
                  <h3 className="font-semibold mb-1">Opis</h3>
                  <p className="text-sm text-gray-300 whitespace-pre-line line-clamp-6">{listing.description}</p>
                </div>
              )}

              {/* Price history chart */}
              {priceHistory && priceHistory.length > 1 && (
                <div>
                  <h3 className="font-semibold mb-2">Historia cen</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={priceHistory}>
                      <XAxis
                        dataKey="recorded_at"
                        tickFormatter={(v) => new Date(v).toLocaleDateString("pl-PL")}
                        tick={{ fontSize: 11, fill: "#666" }}
                      />
                      <YAxis tick={{ fontSize: 11, fill: "#666" }} />
                      <Tooltip
                        labelFormatter={(v) => new Date(v).toLocaleDateString("pl-PL")}
                        formatter={(v) => [`${v} PLN`, "Cena"]}
                        contentStyle={{ background: "#1a1d27", border: "none", borderRadius: 8 }}
                      />
                      <Line type="monotone" dataKey="price" stroke="#f59e0b" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <a
                  href={listing.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-amber text-black font-semibold px-4 py-2 rounded-lg hover:bg-amber/90 transition"
                >
                  Zobacz na Otodom
                </a>
                <a
                  href={`/api/listings/${listing.id}?format=json`}
                  download
                  className="border border-gray-600 px-4 py-2 rounded-lg text-sm text-gray-300 hover:text-white transition"
                >
                  Pobierz JSON
                </a>
                <a
                  href={`/api/listings/${listing.id}?format=xml`}
                  download
                  className="border border-gray-600 px-4 py-2 rounded-lg text-sm text-gray-300 hover:text-white transition"
                >
                  Pobierz XML
                </a>
              </div>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}
