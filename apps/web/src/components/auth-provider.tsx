"use client";

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, type User } from "@/lib/api";
import { useLocale, type AppLocale } from "@/components/locale-provider";

type AuthState = {
  token: string | null;
  user: User | null;
  loading: boolean;
  error: string | null;
  loginDev: () => Promise<void>;
  refresh: () => Promise<void>;
  setUserLocal: (user: User) => void;
};

const AuthContext = createContext<AuthState | null>(null);

function normalizeLocale(value?: string | null): AppLocale | null {
  if (!value) return null;
  const v = value.toLowerCase();
  if (v.startsWith("fa")) return "fa";
  if (v.startsWith("en")) return "en";
  return null;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { setLocale } = useLocale();
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const applyUser = useCallback(
    (next: User) => {
      setUser(next);
      const loc = normalizeLocale(next.locale);
      if (loc) setLocale(loc);
    },
    [setLocale]
  );

  const authenticate = useCallback(
    async (initData: string) => {
      const res = await api.auth(initData);
      setToken(res.access_token);
      localStorage.setItem("ritmo_token", res.access_token);
      applyUser(res.user);
    },
    [applyUser]
  );

  const refresh = useCallback(async () => {
    const saved = localStorage.getItem("ritmo_token");
    if (!saved) return;
    const me = await api.me(saved);
    setToken(saved);
    applyUser(me);
  }, [applyUser]);

  const loginDev = useCallback(async () => {
    await authenticate("dev:10001");
  }, [authenticate]);

  useEffect(() => {
    (async () => {
      try {
        const tg = window.Telegram?.WebApp;
        tg?.ready();
        tg?.expand();
        if (tg?.colorScheme === "dark") {
          document.documentElement.setAttribute("data-tg-color-scheme", "dark");
        }
        if (tg?.initData) {
          await authenticate(tg.initData);
        } else {
          const saved = localStorage.getItem("ritmo_token");
          if (saved) {
            const me = await api.me(saved);
            setToken(saved);
            applyUser(me);
          }
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "auth failed");
      } finally {
        setLoading(false);
      }
    })();
  }, [authenticate, applyUser]);

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      error,
      loginDev,
      refresh,
      setUserLocal: applyUser,
    }),
    [token, user, loading, error, loginDev, refresh, applyUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth outside provider");
  return ctx;
}
