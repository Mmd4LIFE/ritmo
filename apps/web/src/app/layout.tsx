import type { Metadata } from "next";
import { DM_Sans, Vazirmatn } from "next/font/google";
import { cookies } from "next/headers";
import Script from "next/script";
import { AuthProvider } from "@/components/auth-provider";
import { LocaleProvider } from "@/components/locale-provider";
import { AppShell } from "@/components/app-shell";
import "./globals.css";

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
});

const vazirmatn = Vazirmatn({
  subsets: ["arabic"],
  variable: "--font-vazirmatn",
});

export const metadata: Metadata = {
  title: "Ritmo",
  description: "Daily digest, habits, bills, and private cycle tracking",
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const store = await cookies();
  const initialLocale = store.get("NEXT_LOCALE")?.value === "fa" ? "fa" : "en";

  return (
    <html lang={initialLocale} dir={initialLocale === "fa" ? "rtl" : "ltr"} suppressHydrationWarning className={`${dmSans.variable} ${vazirmatn.variable}`}>
      <body className="font-sans antialiased">
        <Script src="https://telegram.org/js/telegram-web-app.js" strategy="beforeInteractive" />
        <LocaleProvider initialLocale={initialLocale}>
          <AuthProvider>
            <AppShell>{children}</AppShell>
          </AuthProvider>
        </LocaleProvider>
      </body>
    </html>
  );
}
