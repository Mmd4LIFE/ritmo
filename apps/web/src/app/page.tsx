"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function HomePage() {
  const t = useTranslations();
  const { token, user, loading, loginDev, error } = useAuth();
  const [summary, setSummary] = useState<Awaited<ReturnType<typeof api.home>> | null>(null);

  useEffect(() => {
    if (!token) return;
    api.home(token).then(setSummary).catch(console.error);
  }, [token]);

  if (loading) {
    return <div className="page text-muted-foreground">{t("common.loading")}</div>;
  }

  if (!token || !user) {
    return (
      <div className="page space-y-6">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Ritmo</p>
          <h1 className="mt-2 text-4xl font-semibold tracking-tight">{t("app.name")}</h1>
          <p className="mt-2 text-muted-foreground">{t("app.tagline")}</p>
        </div>
        {error && <p className="text-sm text-accent">{error}</p>}
        <Button onClick={loginDev}>{t("common.loginDev")}</Button>
      </div>
    );
  }

  return (
    <div className="page space-y-5">
      <header>
        <p className="text-sm text-muted-foreground">{t("home.greeting")}</p>
        <h1 className="text-3xl font-semibold tracking-tight">
          {user.first_name || t("app.name")}
        </h1>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>
            {summary
              ? t("home.streaks", {
                  checked: summary.habits_checked_today,
                  total: summary.habits_active,
                })
              : t("common.loading")}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>{t("home.bestStreak", { n: summary?.streak_best ?? 0 })}</p>
          {summary?.is_premium && <p className="text-primary">{t("home.premium")}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("home.nextBill")}</CardTitle>
        </CardHeader>
        <CardContent className="text-sm">
          {summary?.next_bill ? (
            <p>
              {summary.next_bill.title} — {summary.next_bill.next_due}
            </p>
          ) : (
            <p className="text-muted-foreground">{t("home.noBill")}</p>
          )}
        </CardContent>
      </Card>

      <Button asChild variant="secondary" className="w-full">
        <Link href="/digest">{t("home.openDigest")}</Link>
      </Button>
    </div>
  );
}
