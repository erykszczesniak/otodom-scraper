const PLACEHOLDER_IMG = "https://placehold.co/400x250/1a1d27/666?text=Brak+zdjecia";

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const hours = diff / (1000 * 60 * 60);
  if (hours < 1) return `${Math.round(hours * 60)} min temu`;
  if (hours < 24) return `${Math.round(hours)}h temu`;
  return `${Math.round(hours / 24)}d temu`;
}

export default function ListingCard({ listing, onClick }) {
  let images = [];
  try {
    images = listing.images ? JSON.parse(listing.images) : [];
  } catch {
    images = [];
  }
  const imgUrl = images[0] || PLACEHOLDER_IMG;

  const isNew = (Date.now() - new Date(listing.first_seen).getTime()) < 24 * 60 * 60 * 1000;

  return (
    <div
      onClick={() => onClick?.(listing.id)}
      className="bg-card rounded-xl overflow-hidden cursor-pointer hover:ring-1 hover:ring-amber/50 transition group"
    >
      <div className="relative h-44 overflow-hidden">
        <img
          src={imgUrl}
          alt={listing.title}
          className="w-full h-full object-cover group-hover:scale-105 transition duration-300"
          loading="lazy"
        />
        <div className="absolute top-2 right-2 flex gap-1">
          {isNew && (
            <span className="bg-green-500 text-white text-xs font-bold px-2 py-0.5 rounded">
              NOWE
            </span>
          )}
          {listing.agency_fee === false && (
            <span className="bg-blue-500 text-white text-xs font-bold px-2 py-0.5 rounded">
              BEZ PROWIZJI
            </span>
          )}
        </div>
      </div>

      <div className="p-4 space-y-2">
        <div className="flex items-baseline justify-between">
          <span className="text-2xl font-bold text-amber">
            {listing.price ? `${listing.price.toLocaleString("pl-PL")} PLN` : "Cena nieznana"}
          </span>
          {listing.deposit > 0 && (
            <span className="text-xs text-gray-400">
              Kaucja: {listing.deposit.toLocaleString("pl-PL")} PLN
            </span>
          )}
        </div>

        <h3 className="text-sm font-medium text-gray-200 line-clamp-1">{listing.title}</h3>

        {listing.district && (
          <p className="text-xs text-gray-500">{listing.district}</p>
        )}

        <div className="flex flex-wrap gap-3 text-xs text-gray-400">
          {listing.area && <span>{listing.area} m²</span>}
          {listing.rooms && <span>{listing.rooms} pok.</span>}
          {listing.has_bathtub && <span>🛁 Wanna</span>}
          {listing.pets_allowed && <span>🐾 Zwierzęta</span>}
          {listing.metro_distance_min != null && (
            <span>🚇 {listing.metro_distance_min} min</span>
          )}
          {listing.center_distance_min != null && (
            <span>🏙️ {listing.center_distance_min} min</span>
          )}
        </div>

        <p className="text-xs text-gray-600">{timeAgo(listing.first_seen)}</p>
      </div>
    </div>
  );
}
