"use client";

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, type User } from "@/lib/api";

type AuthState = {
  token: string | null;
  user: User | null;
  loading: boolean;
  error: string | null;
  loginDev: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData: string;
        ready: () => void;
        expand: () => void;
        themeParams: Record<string, string>;
        colorScheme: string;
        openInvoice?: (url: string, cb?: (status: string) => void) => void;
      };
    };
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const authenticate = useCallback(async (initData: string) => {
    const res = await api.auth(initData);
    setToken(res.access_token);
    setUser(res.user);
    localStorage.setItem("ritmo_token", res.access_token);
    if (res.user.locale) {
      document.cookie = `NEXT_LOCALE=${res.user.locale};path=/;max-age=31536000`;
    }
  }, []);

  const refresh = useCallback(async () => {
    const saved = localStorage.getItem("ritmo_token");
    if (!saved) return;
    const me = await api.me(saved);
    setToken(saved);
    setUser(me);
  }, []);

  const loginDev = useCallback(async () => {
    await authenticate("dev:10001");
  }, [authenticate]);

  useEffect(() => {
    (async () => {
      try {
        const tg = window.Telegram?.WebApp;
        tg?.ready();
        tg?.expand();
        if (tg?.initData) {
          await authenticate(tg.initData);
        } else {
          const saved = localStorage.getItem("ritmo_token");
          if (saved) {
            const me = await api.me(saved);
            setToken(saved);
            setUser(me);
          }
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "auth failed");
      } finally {
        setLoading(false);
      }
    })();
  }, [authenticate]);

  const value = useMemo(
    () => ({ token, user, loading, error, loginDev, refresh }),
    [token, user, loading, error, loginDev, refresh]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth outside provider");
  return ctx;
}
