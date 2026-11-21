"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/components/auth-provider";
import { useLocale, type AppLocale } from "@/components/locale-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

export default function ProfilePage() {
  const t = useTranslations("profile");
  const tc = useTranslations("common");
  const { token, user, refresh } = useAuth();
  const { locale, setLocale } = useLocale();
  const [timezone, setTimezone] = useState("Asia/Tehran");
  const [status, setStatus] = useState<{ is_premium: boolean; ends_at?: string } | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (user?.timezone) setTimezone(user.timezone);
  }, [user]);

  useEffect(() => {
    if (!token) return;
    api.billing.status(token).then(setStatus).catch(console.error);
  }, [token]);

  if (!token || !user) return <div className="page" />;

  const changeLanguage = async (next: AppLocale) => {
    setLocale(next);
    await api.patchMe(token, { locale: next });
    await refresh();
    setSaved(true);
  };

  return (
    <div className="page space-y-4">
      <h1 className="text-2xl font-semibold">{t("title")}</h1>

      <Card>
        <CardHeader>
          <CardTitle>{user.first_name || user.username || "User"}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div>
            <label className="mb-2 block font-medium">{t("language")}</label>
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant={locale === "fa" ? "default" : "outline"}
                onClick={() => changeLanguage("fa")}
              >
                فارسی
              </Button>
              <Button
                variant={locale === "en" ? "default" : "outline"}
                onClick={() => changeLanguage("en")}
              >
                English
              </Button>
            </div>
          </div>
          <div>
            <label className="mb-1 block font-medium">{t("timezone")}</label>
            <Input value={timezone} onChange={(e) => setTimezone(e.target.value)} />
          </div>
          <Button
            className="w-full"
            onClick={async () => {
              await api.patchMe(token, { timezone, locale });
              await refresh();
              setSaved(true);
            }}
          >
            {tc("save")}
          </Button>
          {saved && <p className="text-center text-xs text-primary">{t("saved")}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{status?.is_premium ? t("premiumActive") : t("upgrade")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          {status?.is_premium ? <p>{status.ends_at}</p> : <p>{t("premiumHint")}</p>}
        </CardContent>
      </Card>
    </div>
  );
}
