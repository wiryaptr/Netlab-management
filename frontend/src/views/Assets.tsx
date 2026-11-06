import React, { useEffect, useState } from "react";
import { api } from "../api";
import { useApp } from "../context";

interface Asset {
  id: number;
  name: string;
  asset_type: string;
  status: string;
  location_name: string | null;
  serial_number: string | null;
}

export const AssetsView: React.FC = () => {
  const { can } = useApp();
  const [items, setItems] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [type, setType] = useState("switch");
  const [status, setStatus] = useState("in_use");

  const load = () => {
    setLoading(true);
    api<{ results: Asset[] }>("/assets/")
      .then((r) => setItems(r.results || []))
      .catch((e) => alert(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api("/assets/", { method: "POST", body: { name, asset_type: type, status } });
      setName("");
      load();
    } catch (err: unknown) {
      alert((err as Error).message);
    }
  };

  const archive = async (id: number) => {
    if (!confirm("Arsipkan aset ini?")) return;
    try {
      await api(`/assets/${id}/archive/`, { method: "POST" });
      load();
    } catch (err: unknown) {
      alert((err as Error).message);
    }
  };

  return (
    <div>
      <h2>Aset Perangkat Jaringan</h2>
      {can("assets.add_asset") && (
        <form onSubmit={create} style={{ marginBottom: 16, display: "flex", gap: 8 }}>
          <input
            placeholder="Nama Aset (contoh: SW-CORE-01)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <select value={type} onChange={(e) => setType(e.target.value)}>
            <option value="switch">Switch</option>
            <option value="router">Router</option>
            <option value="server">Server</option>
            <option value="firewall">Firewall</option>
            <option value="access_point">Access Point</option>
          </select>
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="in_use">In Use</option>
            <option value="spare">Spare</option>
            <option value="maintenance">Maintenance</option>
          </select>
          <button type="submit">Tambah Aset</button>
        </form>
      )}

      {loading ? (
        <div>Memuat aset...</div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }} border={1}>
          <thead>
            <tr style={{ background: "#eee" }}>
              <th>ID</th>
              <th>Nama</th>
              <th>Tipe</th>
              <th>Status</th>
              <th>Lokasi</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.id}>
                <td>{it.id}</td>
                <td>{it.name}</td>
                <td>{it.asset_type}</td>
                <td>{it.status}</td>
                <td>{it.location_name || "-"}</td>
                <td>
                  {can("assets.archive_asset") && (
                    <button onClick={() => archive(it.id)}>Arsipkan</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
