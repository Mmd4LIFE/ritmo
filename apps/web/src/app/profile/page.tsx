"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

export default function ProfilePage() {
  const t = useTranslations("profile");
  const { token, user, refresh } = useAuth();
  const [locale, setLocale] = useState("en");
  const [timezone, setTimezone] = useState("Asia/Tehran");
  const [status, setStatus] = useState<{ is_premium: boolean; ends_at?: string } | null>(null);

  useEffect(() => {
    if (user) {
      setLocale(user.locale);
      setTimezone(user.timezone);
    }
  }, [user]);

  useEffect(() => {
    if (!token) return;
    api.billing.status(token).then(setStatus).catch(console.error);
  }, [token]);

  if (!token || !user) return <div className="page" />;

  return (
    <div className="page space-y-4">
      <h1 className="text-2xl font-semibold">{t("title")}</h1>

      <Card>
        <CardHeader>
          <CardTitle>
            {user.first_name || user.username || "User"}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div>
            <label className="mb-1 block">{t("language")}</label>
            <div className="flex gap-2">
              <Button variant={locale === "en" ? "default" : "outline"} onClick={() => setLocale("en")}>
                English
              </Button>
              <Button variant={locale === "fa" ? "default" : "outline"} onClick={() => setLocale("fa")}>
                فارسی
              </Button>
            </div>
          </div>
          <div>
            <label className="mb-1 block">{t("timezone")}</label>
            <Input value={timezone} onChange={(e) => setTimezone(e.target.value)} />
          </div>
          <Button
            className="w-full"
            onClick={async () => {
              await api.patchMe(token, { locale, timezone });
              document.cookie = `NEXT_LOCALE=${locale};path=/;max-age=31536000`;
              await refresh();
              window.location.reload();
            }}
          >
            Save
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{status?.is_premium ? t("premiumActive") : t("upgrade")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          {status?.is_premium ? (
            <p>{status.ends_at}</p>
          ) : (
            <p>Open the bot and send /premium to pay with Telegram Stars.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
