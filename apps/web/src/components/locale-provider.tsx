"use client";

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { NextIntlClientProvider } from "next-intl";
import en from "../../messages/en.json";
import fa from "../../messages/fa.json";

export type AppLocale = "en" | "fa";

const catalogs = { en, fa } as const;

type LocaleContextValue = {
  locale: AppLocale;
  setLocale: (locale: AppLocale, opts?: { persistCookie?: boolean }) => void;
  dir: "rtl" | "ltr";
};

const LocaleContext = createContext<LocaleContextValue | null>(null);

function applyDocumentLocale(locale: AppLocale) {
  document.documentElement.lang = locale;
  document.documentElement.dir = locale === "fa" ? "rtl" : "ltr";
  document.cookie = `NEXT_LOCALE=${locale};path=/;max-age=31536000;SameSite=Lax`;
  try {
    localStorage.setItem("ritmo_locale", locale);
  } catch {
    /* ignore */
  }
}

function detectInitialLocale(serverLocale?: string): AppLocale {
  if (typeof window !== "undefined") {
    try {
      const stored = localStorage.getItem("ritmo_locale");
      if (stored === "fa" || stored === "en") return stored;
    } catch {
      /* ignore */
    }
    const tgLang = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code;
    if (tgLang?.toLowerCase().startsWith("fa")) return "fa";
  }
  if (serverLocale === "fa") return "fa";
  return "en";
}

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData: string;
        initDataUnsafe?: { user?: { language_code?: string } };
        ready: () => void;
        expand: () => void;
        themeParams: Record<string, string>;
        colorScheme: string;
        openInvoice?: (url: string, cb?: (status: string) => void) => void;
      };
    };
  }
}

export function LocaleProvider({
  children,
  initialLocale = "en",
}: {
  children: React.ReactNode;
  initialLocale?: string;
}) {
  const [locale, setLocaleState] = useState<AppLocale>(() =>
    detectInitialLocale(initialLocale)
  );

  useEffect(() => {
    applyDocumentLocale(locale);
  }, [locale]);

  const setLocale = useCallback((next: AppLocale) => {
    setLocaleState(next);
    applyDocumentLocale(next);
  }, []);

  const value = useMemo(
    () => ({ locale, setLocale, dir: locale === "fa" ? ("rtl" as const) : ("ltr" as const) }),
    [locale, setLocale]
  );

  return (
    <LocaleContext.Provider value={value}>
      <NextIntlClientProvider locale={locale} messages={catalogs[locale]} timeZone="Asia/Tehran">
        {children}
      </NextIntlClientProvider>
    </LocaleContext.Provider>
  );
}

export function useLocale() {
  const ctx = useContext(LocaleContext);
  if (!ctx) throw new Error("useLocale outside provider");
  return ctx;
}
