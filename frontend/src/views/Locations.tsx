import React, { useEffect, useState } from "react";
import { api } from "../api";
import { useApp } from "../context";

interface Location {
  id: number;
  name: string;
  location_type: string;
  description: string;
}

export const LocationsView: React.FC = () => {
  const { can } = useApp();
  const [items, setItems] = useState<Location[]>([]);
  const [name, setName] = useState("");
  const [type, setType] = useState("room");
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    api<{ results: Location[] }>("/locations/")
      .then((r) => setItems(r.results || []))
      .catch((e) => alert(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api("/locations/", { method: "POST", body: { name, location_type: type } });
      setName("");
      load();
    } catch (err: unknown) {
      alert((err as Error).message);
    }
  };

  return (
    <div>
      <h2>Lokasi Laboratorium</h2>
      {can("locations.add_location") && (
        <form onSubmit={create} style={{ marginBottom: 16, display: "flex", gap: 8 }}>
          <input placeholder="Nama Lokasi" value={name} onChange={(e) => setName(e.target.value)} required />
          <select value={type} onChange={(e) => setType(e.target.value)}>
            <option value="room">Room</option>
            <option value="building">Building</option>
            <option value="rack">Rack</option>
            <option value="cabinet">Cabinet</option>
            <option value="storage">Storage</option>
            <option value="other">Other</option>
          </select>
          <button type="submit">Tambah Lokasi</button>
        </form>
      )}
      {loading ? (
        <div>Memuat lokasi...</div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }} border={1}>
          <thead>
            <tr style={{ background: "#eee" }}>
              <th>ID</th>
              <th>Nama</th>
              <th>Tipe</th>
              <th>Deskripsi</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.id}>
                <td>{it.id}</td>
                <td>{it.name}</td>
                <td>{it.location_type}</td>
                <td>{it.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
