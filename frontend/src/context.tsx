import React, { createContext, useContext, useEffect, useState } from "react";
import { api, Me } from "./api";

export type View =
  | "dashboard"
  | "assets"
  | "locations"
  | "subnets"
  | "ip-addresses"
  | "vlans"
  | "connections"
  | "incidents"
  | "imports"
  | "audit"
  | "users";

interface Ctx {
  user: Me | null;
  view: View;
  setView: (v: View) => void;
  logout: () => Promise<void>;
  can: (perm: string) => boolean;
}

const AppCtx = createContext<Ctx>({
  user: null,
  view: "dashboard",
  setView: () => {},
  logout: async () => {},
  can: () => false,
});

export const useApp = () => useContext(AppCtx);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<Me | null>(null);
  const [view, setView] = useState<View>("dashboard");

  useEffect(() => {
    api<Me>("/auth/me/")
      .then(setUser)
      .catch(() => {});
  }, []);

  const doLogout = async () => {
    await api<void>("/auth/logout/", { method: "POST" }).catch(() => {});
    setUser(null);
  };

  const can = (perm: string) => {
    if (!user) return false;
    if (user.role === "administrator") return true;
    return user.permissions.includes(perm);
  };

  return (
    <AppCtx.Provider value={{ user, view, setView, logout: doLogout, can }}>
      {children}
    </AppCtx.Provider>
  );
};
