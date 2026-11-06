import React, { useEffect, useState } from "react";
import { api } from "../api";
import { useApp } from "../context";

interface Incident {
  id: number;
  title: string;
  severity: string;
  status: string;
  asset_name: string | null;
  assignee_username: string | null;
  created_at: string;
}

export const IncidentsView: React.FC = () => {
  const { can } = useApp();
  const [items, setItems] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [severity, setSeverity] = useState("medium");

  const load = () => {
    setLoading(true);
    api<{ results: Incident[] }>("/incidents/")
      .then((r) => setItems(r.results || []))
      .catch((e) => alert(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api("/incidents/", { method: "POST", body: { title, severity } });
      setTitle("");
      load();
    } catch (err: unknown) {
      alert((err as Error).message);
    }
  };

  const closeIncident = async (id: number) => {
    try {
      await api(`/incidents/${id}/`, { method: "PATCH", body: { status: "closed" } });
      load();
    } catch (err: unknown) {
      alert((err as Error).message);
    }
  };

  return (
    <div>
      <h2>Tiket Gangguan / Insiden</h2>
      {can("incidents.add_incident") && (
        <form onSubmit={create} style={{ marginBottom: 16, display: "flex", gap: 8 }}>
          <input
            placeholder="Judul Insiden (misal: Kabel putus di Lab A)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            style={{ width: 300 }}
          />
          <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
          <button type="submit">Buka Insiden</button>
        </form>
      )}

      {loading ? (
        <div>Memuat insiden...</div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }} border={1}>
          <thead>
            <tr style={{ background: "#eee" }}>
              <th>ID</th>
              <th>Judul</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Aset</th>
              <th>Petugas</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.id}>
                <td>{it.id}</td>
                <td>{it.title}</td>
                <td>{it.severity}</td>
                <td>{it.status}</td>
                <td>{it.asset_name || "-"}</td>
                <td>{it.assignee_username || "-"}</td>
                <td>
                  {it.status !== "closed" && can("incidents.change_status_incident") && (
                    <button onClick={() => closeIncident(it.id)}>Tutup (Close)</button>
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
