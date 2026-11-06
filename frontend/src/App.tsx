import React from "react";
import { AppProvider, useApp } from "./context";
import { Dashboard } from "./views/Dashboard";
import { AssetsView } from "./views/Assets";
import { LocationsView } from "./views/Locations";
import { IncidentsView } from "./views/Incidents";
import { ImportsView } from "./views/Imports";

const Main: React.FC = () => {
  const { view, setView, user, logout } = useApp();

  if (!user) return <div style={{ padding: 40 }}>Harap login terlebih dahulu.</div>;

  const menu = [
    { id: "dashboard", label: "Dashboard" },
    { id: "assets", label: "Aset" },
    { id: "locations", label: "Lokasi" },
    { id: "incidents", label: "Insiden" },
    { id: "imports", label: "Impor CSV" },
  ];

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <nav style={{ width: 200, background: "#333", color: "#fff", padding: 20 }}>
        <h2>NetLab</h2>
        <ul style={{ listStyle: "none", padding: 0 }}>
          {menu.map((m) => (
            <li key={m.id} style={{ marginBottom: 10 }}>
              <button
                onClick={() => setView(m.id as any)}
                style={{
                  background: view === m.id ? "#555" : "transparent",
                  color: "#fff",
                  border: "none",
                  width: "100%",
                  textAlign: "left",
                  padding: 10,
                  cursor: "pointer",
                }}
              >
                {m.label}
              </button>
            </li>
          ))}
        </ul>
        <button onClick={logout} style={{ marginTop: 20, color: "red" }}>Keluar</button>
      </nav>
      <main style={{ flex: 1, padding: 40 }}>
        {view === "dashboard" && <Dashboard />}
        {view === "assets" && <AssetsView />}
        {view === "locations" && <LocationsView />}
        {view === "incidents" && <IncidentsView />}
        {view === "imports" && <ImportsView />}
      </main>
    </div>
  );
};

export default function App() {
  return (
    <AppProvider>
      <Main />
    </AppProvider>
  );
}
