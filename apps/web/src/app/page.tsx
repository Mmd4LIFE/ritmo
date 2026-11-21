"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { useAuth } from "@/components/auth-provider";
import { Onboarding } from "@/components/onboarding";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function HomePage() {
  const t = useTranslations();
  const { token, user, loading, loginDev, error, refresh } = useAuth();
  const [summary, setSummary] = useState<Awaited<ReturnType<typeof api.home>> | null>(null);
  const [forceOnboarding, setForceOnboarding] = useState(false);

  useEffect(() => {
    if (!token || !user?.onboarding_done || forceOnboarding) return;
    api.home(token).then(setSummary).catch(console.error);
  }, [token, user?.onboarding_done, forceOnboarding]);

  if (loading) {
    return <div className="page text-muted-foreground">{t("common.loading")}</div>;
  }

  if (!token || !user) {
    return (
      <div className="page space-y-6">
        <div>
          <p className="text-sm tracking-[0.18em] text-muted-foreground uppercase">Ritmo</p>
          <h1 className="mt-2 text-4xl font-semibold tracking-tight">{t("app.name")}</h1>
          <p className="mt-3 text-muted-foreground leading-relaxed">{t("app.tagline")}</p>
        </div>
        {error && <p className="text-sm text-accent">{error}</p>}
        <Button className="w-full" size="lg" onClick={loginDev}>
          {t("common.loginDev")}
        </Button>
      </div>
    );
  }

  if (!user.onboarding_done || forceOnboarding) {
    return (
      <Onboarding
        onDone={async () => {
          setForceOnboarding(false);
          await refresh();
        }}
      />
    );
  }

  return (
    <div className="page space-y-5">
      <header className="space-y-1">
        <p className="text-sm text-muted-foreground">{t("home.greeting")}</p>
        <h1 className="text-3xl font-semibold tracking-tight">
          {user.first_name || t("app.name")}
        </h1>
        <p className="text-sm text-muted-foreground">{t("home.whatIsThis")}</p>
      </header>

      <div className="grid grid-cols-3 gap-2">
        <Link href="/habits" className="rounded-xl border border-border bg-card p-3 text-center text-sm font-medium">
          {t("home.quickHabits")}
        </Link>
        <Link href="/bills" className="rounded-xl border border-border bg-card p-3 text-center text-sm font-medium">
          {t("home.quickBills")}
        </Link>
        <Link href="/digest" className="rounded-xl border border-border bg-card p-3 text-center text-sm font-medium">
          {t("home.quickDigest")}
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t("home.subtitle")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>
            {summary
              ? t("home.streaks", {
                  checked: summary.habits_checked_today,
                  total: summary.habits_active,
                })
              : t("common.loading")}
          </p>
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

      <button
        type="button"
        className="w-full text-center text-xs text-muted-foreground underline"
        onClick={() => setForceOnboarding(true)}
      >
        {t("home.setupAgain")}
      </button>
    </div>
  );
}
