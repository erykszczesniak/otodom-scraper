import { useState } from "react";

const DISTRICTS = [
  "Bemowo", "Białołęka", "Bielany", "Mokotów", "Ochota",
  "Praga-Południe", "Praga-Północ", "Rembertów", "Śródmieście",
  "Targówek", "Ursus", "Ursynów", "Wawer", "Wesoła",
  "Wilanów", "Włochy", "Wola", "Żoliborz",
];

export default function FilterPanel({ filters, setFilters, onReset }) {
  const [local, setLocal] = useState(filters);

  const update = (key, value) => {
    setLocal((prev) => ({ ...prev, [key]: value }));
  };

  const toggleRoom = (room) => {
    setLocal((prev) => {
      const rooms = prev.rooms || [];
      if (rooms.includes(room)) {
        return { ...prev, rooms: rooms.filter((r) => r !== room) };
      }
      return { ...prev, rooms: [...rooms, room] };
    });
  };

  const apply = () => setFilters(local);

  const reset = () => {
    const empty = {};
    setLocal(empty);
    setFilters(empty);
    onReset?.();
  };

  const activeCount = Object.values(local).filter(
    (v) => v !== null && v !== undefined && v !== "" && !(Array.isArray(v) && v.length === 0)
  ).length;

  return (
    <aside className="w-72 bg-card rounded-xl p-5 h-fit sticky top-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Filtry</h2>
        {activeCount > 0 && (
          <span className="bg-amber text-black text-xs font-bold px-2 py-0.5 rounded-full">
            {activeCount}
          </span>
        )}
      </div>

      <div>
        <label className="text-sm text-gray-400">Cena (PLN)</label>
        <div className="flex gap-2 mt-1">
          <input
            type="number"
            placeholder="Min"
            value={local.price_min || ""}
            onChange={(e) => update("price_min", e.target.value || null)}
            className="w-full bg-bg border border-gray-700 rounded px-2 py-1 text-sm"
          />
          <input
            type="number"
            placeholder="Max"
            value={local.price_max || ""}
            onChange={(e) => update("price_max", e.target.value || null)}
            className="w-full bg-bg border border-gray-700 rounded px-2 py-1 text-sm"
          />
        </div>
      </div>

      <div>
        <label className="text-sm text-gray-400">Metraż (m²)</label>
        <div className="flex gap-2 mt-1">
          <input
            type="number"
            placeholder="Min"
            value={local.area_min || ""}
            onChange={(e) => update("area_min", e.target.value || null)}
            className="w-full bg-bg border border-gray-700 rounded px-2 py-1 text-sm"
          />
          <input
            type="number"
            placeholder="Max"
            value={local.area_max || ""}
            onChange={(e) => update("area_max", e.target.value || null)}
            className="w-full bg-bg border border-gray-700 rounded px-2 py-1 text-sm"
          />
        </div>
      </div>

      <div>
        <label className="text-sm text-gray-400">Pokoje</label>
        <div className="flex gap-2 mt-1">
          {[1, 2, 3, 4].map((r) => (
            <button
              key={r}
              onClick={() => toggleRoom(r)}
              className={`px-3 py-1 rounded text-sm font-medium transition ${
                (local.rooms || []).includes(r)
                  ? "bg-amber text-black"
                  : "bg-bg border border-gray-700 text-gray-300"
              }`}
            >
              {r === 4 ? "4+" : r}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="text-sm text-gray-400">Dzielnica</label>
        <select
          value={local.district || ""}
          onChange={(e) => update("district", e.target.value || null)}
          className="w-full bg-bg border border-gray-700 rounded px-2 py-1 text-sm mt-1"
        >
          <option value="">Wszystkie</option>
          {DISTRICTS.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={local.has_bathtub === true}
            onChange={(e) => update("has_bathtub", e.target.checked ? true : null)}
            className="accent-amber"
          />
          Wanna
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={local.pets_allowed === true}
            onChange={(e) => update("pets_allowed", e.target.checked ? true : null)}
            className="accent-amber"
          />
          Zwierzęta
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={local.agency_fee === false}
            onChange={(e) => update("agency_fee", e.target.checked ? false : null)}
            className="accent-amber"
          />
          Bez prowizji
        </label>
      </div>

      <div>
        <label className="text-sm text-gray-400">Max min do metra</label>
        <input
          type="number"
          value={local.metro_max_min || ""}
          onChange={(e) => update("metro_max_min", e.target.value || null)}
          className="w-full bg-bg border border-gray-700 rounded px-2 py-1 text-sm mt-1"
        />
      </div>

      <div>
        <label className="text-sm text-gray-400">Max min do centrum</label>
        <input
          type="number"
          value={local.center_max_min || ""}
          onChange={(e) => update("center_max_min", e.target.value || null)}
          className="w-full bg-bg border border-gray-700 rounded px-2 py-1 text-sm mt-1"
        />
      </div>

      <div className="flex gap-2 pt-2">
        <button
          onClick={apply}
          className="flex-1 bg-amber text-black font-semibold py-2 rounded-lg hover:bg-amber/90 transition"
        >
          Szukaj
        </button>
        <button
          onClick={reset}
          className="px-3 py-2 border border-gray-600 rounded-lg text-sm text-gray-400 hover:text-white transition"
        >
          Reset
        </button>
      </div>
    </aside>
  );
}
