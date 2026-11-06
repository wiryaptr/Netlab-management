import React, { useEffect, useState } from "react";
import { api } from "../api";

interface Summary {
  locations: number;
  assets: number;
  subnets: number;
  ip_addresses: number;
  vlans: number;
  connections: number;
  open_incidents: number;
}

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<Summary | null>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api<Summary>("/dashboard/summary/")
      .then(setData)
      .catch((e) => setErr(e.message));
  }, []);

  if (err) return <div style={{ color: "red" }}>Gagal memuat dashboard: {err}</div>;
  if (!data) return <div>Memuat ringkasan...</div>;

  const card = (label: string, value: number, warn = false) => (
    <div
      style={{
        padding: 16,
        borderRadius: 8,
        border: "1px solid #ddd",
        minWidth: 160,
        backgroundColor: warn && value > 0 ? "#fff3cd" : "#fff",
      }}
    >
      <div style={{ fontSize: 12, color: "#666" }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: "bold" }}>{value}</div>
    </div>
  );

  return (
    <div>
      <h2>Ringkasan Operasional Laboratorium</h2>
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginTop: 16 }}>
        {card("Lokasi Aktif", data.locations)}
        {card("Aset Aktif", data.assets)}
        {card("Subnet", data.subnets)}
        {card("Alamat IP", data.ip_addresses)}
        {card("VLAN", data.vlans)}
        {card("Koneksi", data.connections)}
        {card("Insiden Terbuka", data.open_incidents, true)}
      </div>
    </div>
  );
};
