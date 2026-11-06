import React, { useState } from "react";
import { uploadCsvImport } from "../api";
import { useApp } from "../context";

export const ImportsView: React.FC = () => {
  const { can } = useApp();
  const [file, setFile] = useState<File | null>(null);
  const [resource, setResource] = useState("locations");
  const [res, setRes] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handle = async (mode: "preview" | "commit") => {
    if (!file) return;
    setLoading(true);
    setRes(null);
    try {
      const data = await uploadCsvImport(file, resource, mode);
      setRes(data);
    } catch (e: any) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (!can("imports.import_locations") && !can("imports.import_assets")) {
    return <div>Anda tidak memiliki izin untuk mengimpor CSV.</div>;
  }

  return (
    <div>
      <h2>Impor Data dari CSV</h2>
      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        <select value={resource} onChange={(e) => setResource(e.target.value)}>
          <option value="locations">Locations</option>
          <option value="assets">Assets</option>
          <option value="subnets">Subnets</option>
          <option value="ip-addresses">IP Addresses</option>
        </select>
        <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button disabled={loading || !file} onClick={() => handle("preview")}>
          Preview
        </button>
        <button
          disabled={loading || !file}
          onClick={() => handle("commit")}
          style={{ background: "#28a745", color: "#fff" }}
        >
          Commit (Simpan)
        </button>
      </div>

      {loading && <div>Memproses...</div>}

      {res && (
        <div style={{ background: "#f8f9fa", padding: 16, borderRadius: 8, border: "1px solid #ddd" }}>
          <h4>Hasil: {res.mode}</h4>
          <p>
            Total baris: {res.summary.rows} | Valid: {res.summary.valid} | Error: {res.summary.errors}
          </p>
          {res.created > 0 && (
            <p style={{ color: "green", fontWeight: "bold" }}>
              Berhasil membuat {res.created} data baru.
            </p>
          )}
          {res.errors.length > 0 && (
            <div style={{ color: "red" }}>
              <h5>Daftar Error:</h5>
              <ul>
                {res.errors.map((e: any, i: number) => (
                  <li key={i}>
                    Baris {e.row}: {e.message} ({e.column})
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
