import { useStats } from "../hooks/useListings";

export default function StatsBar() {
  const { data: stats } = useStats();

  if (!stats || stats.count_active === 0) return null;

  const items = [
    { label: "Ogłoszenia", value: stats.count_active },
    { label: "Śr. cena", value: stats.avg_price ? `${Math.round(stats.avg_price).toLocaleString("pl-PL")} PLN` : "—" },
    { label: "Mediana", value: stats.median_price ? `${Math.round(stats.median_price).toLocaleString("pl-PL")} PLN` : "—" },
    { label: "PLN/m²", value: stats.price_per_m2_avg ? `${Math.round(stats.price_per_m2_avg).toLocaleString("pl-PL")}` : "—" },
    { label: "Z wanną", value: `${Math.round((stats.count_with_bathtub / stats.count_active) * 100)}%` },
    { label: "Zwierzęta OK", value: `${Math.round((stats.count_pets_allowed / stats.count_active) * 100)}%` },
  ];

  return (
    <div className="flex flex-wrap gap-6 text-sm">
      {items.map((item) => (
        <div key={item.label}>
          <span className="text-gray-500">{item.label}: </span>
          <span className="text-white font-medium">{item.value}</span>
        </div>
      ))}
    </div>
  );
}
