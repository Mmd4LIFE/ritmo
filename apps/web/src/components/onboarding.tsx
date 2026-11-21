"use client";

import { useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/components/auth-provider";
import { useLocale, type AppLocale } from "@/components/locale-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

const TOTAL = 7;

const HABIT_PRESETS = [
  { kind: "water", emoji: "💧" },
  { kind: "study", emoji: "📚" },
  { kind: "gym", emoji: "🏋️" },
  { kind: "no_smoking", emoji: "🚭" },
] as const;

export function Onboarding({ onDone }: { onDone: () => void }) {
  const t = useTranslations("onboarding");
  const th = useTranslations("habits");
  const { token, refresh } = useAuth();
  const { locale, setLocale } = useLocale();
  const [step, setStep] = useState(0);
  const [busy, setBusy] = useState(false);
  const [city, setCity] = useState(locale === "fa" ? "تهران" : "Tehran");
  const [hour, setHour] = useState(8);
  const [selectedHabits, setSelectedHabits] = useState<string[]>(["water"]);
  const [billTitle, setBillTitle] = useState("");
  const [billDue, setBillDue] = useState("");

  const progress = useMemo(() => ((step + 1) / TOTAL) * 100, [step]);

  const next = () => setStep((s) => Math.min(TOTAL - 1, s + 1));
  const back = () => setStep((s) => Math.max(0, s - 1));

  const pickLanguage = async (nextLocale: AppLocale) => {
    setLocale(nextLocale);
    if (token) {
      await api.patchMe(token, { locale: nextLocale, timezone: "Asia/Tehran" });
      await refresh();
    }
    if (nextLocale === "fa" && (city === "Tehran" || !city)) setCity("تهران");
    if (nextLocale === "en" && (city === "تهران" || !city)) setCity("Tehran");
    next();
  };

  const saveCityHour = async () => {
    if (!token) return;
    setBusy(true);
    try {
      await api.patchMe(token, { city: city.trim() || null });
      await api.digest.patch(token, {
        city: city.trim() || null,
        hour,
        enabled: true,
        price_symbols: ["USD/IRR"],
        news_topic: "technology",
      });
      await refresh();
      next();
    } finally {
      setBusy(false);
    }
  };

  const saveHabits = async () => {
    if (!token) return;
    setBusy(true);
    try {
      const existing = await api.habits.list(token);
      const have = new Set(existing.map((h) => h.kind));
      for (const kind of selectedHabits) {
        if (have.has(kind)) continue;
        const preset = HABIT_PRESETS.find((p) => p.kind === kind);
        await api.habits.create(token, {
          kind,
          title: th(`kinds.${kind}`),
          emoji: preset?.emoji,
        });
      }
      next();
    } finally {
      setBusy(false);
    }
  };

  const saveBill = async (skip: boolean) => {
    if (!token) return;
    setBusy(true);
    try {
      if (!skip && billTitle.trim() && billDue) {
        await api.bills.create(token, {
          title: billTitle.trim(),
          next_due: billDue,
          warn_days: 3,
          recurrence: "monthly",
          currency: "IRR",
        });
      }
      next();
    } finally {
      setBusy(false);
    }
  };

  const saveCycle = async (enable: boolean) => {
    if (!token) return;
    setBusy(true);
    try {
      if (enable) {
        await api.cycle.patch(token, { reminders_enabled: true });
        await api.patchMe(token, { notify_cycle: true });
      } else {
        await api.cycle.patch(token, { reminders_enabled: false });
        await api.patchMe(token, { notify_cycle: false });
      }
      next();
    } finally {
      setBusy(false);
    }
  };

  const finish = async () => {
    if (!token) return;
    setBusy(true);
    try {
      await api.patchMe(token, { onboarding_done: true, locale });
      await refresh();
      onDone();
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page space-y-6 pb-10">
      <div className="space-y-2">
        <p className="text-xs text-muted-foreground">{t("step", { current: step + 1, total: TOTAL })}</p>
        <div className="h-1.5 overflow-hidden rounded-full bg-muted">
          <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {step === 0 && (
        <section className="space-y-5">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">{t("welcomeTitle")}</h1>
            <p className="mt-3 text-muted-foreground leading-relaxed">{t("welcomeBody")}</p>
          </div>
          <ul className="space-y-3 text-sm">
            {[1, 2, 3, 4].map((n) => (
              <li key={n} className="flex gap-3 rounded-xl border border-border bg-card/80 p-3">
                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/15 text-xs font-semibold text-primary">
                  {n}
                </span>
                <span>{t(`welcomePoint${n}` as "welcomePoint1")}</span>
              </li>
            ))}
          </ul>
          <Button className="w-full" size="lg" onClick={next}>
            {t("continue")}
          </Button>
        </section>
      )}

      {step === 1 && (
        <section className="space-y-5">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">{t("languageTitle")}</h1>
            <p className="mt-2 text-muted-foreground">{t("languageBody")}</p>
          </div>
          <div className="grid gap-3">
            <Button
              size="lg"
              variant={locale === "fa" ? "default" : "outline"}
              className="h-14 text-base"
              onClick={() => pickLanguage("fa")}
            >
              فارسی
            </Button>
            <Button
              size="lg"
              variant={locale === "en" ? "default" : "outline"}
              className="h-14 text-base"
              onClick={() => pickLanguage("en")}
            >
              English
            </Button>
          </div>
          <Button variant="ghost" onClick={back}>
            {t("back")}
          </Button>
        </section>
      )}

      {step === 2 && (
        <section className="space-y-5">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">{t("cityTitle")}</h1>
            <p className="mt-2 text-muted-foreground">{t("cityBody")}</p>
          </div>
          <Input
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder={t("cityPlaceholder")}
          />
          <div>
            <p className="mb-2 text-sm font-medium">{t("hourTitle")}</p>
            <p className="mb-3 text-sm text-muted-foreground">{t("hourBody")}</p>
            <Input
              type="number"
              min={0}
              max={23}
              value={hour}
              onChange={(e) => setHour(Number(e.target.value))}
            />
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="flex-1" onClick={back}>
              {t("back")}
            </Button>
            <Button className="flex-1" disabled={busy} onClick={saveCityHour}>
              {t("continue")}
            </Button>
          </div>
        </section>
      )}

      {step === 3 && (
        <section className="space-y-5">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">{t("habitsTitle")}</h1>
            <p className="mt-2 text-muted-foreground">{t("habitsBody")}</p>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {HABIT_PRESETS.map((p) => {
              const active = selectedHabits.includes(p.kind);
              return (
                <button
                  key={p.kind}
                  type="button"
                  onClick={() =>
                    setSelectedHabits((prev) =>
                      active ? prev.filter((k) => k !== p.kind) : [...prev, p.kind]
                    )
                  }
                  className={cn(
                    "rounded-xl border p-4 text-start transition",
                    active ? "border-primary bg-primary/10" : "border-border bg-card"
                  )}
                >
                  <div className="text-2xl">{p.emoji}</div>
                  <div className="mt-2 font-medium">{th(`kinds.${p.kind}`)}</div>
                </button>
              );
            })}
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="flex-1" onClick={back}>
              {t("back")}
            </Button>
            <Button className="flex-1" disabled={busy || selectedHabits.length === 0} onClick={saveHabits}>
              {t("continue")}
            </Button>
          </div>
        </section>
      )}

      {step === 4 && (
        <section className="space-y-5">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">{t("billsTitle")}</h1>
            <p className="mt-2 text-muted-foreground">{t("billsBody")}</p>
          </div>
          <Input
            value={billTitle}
            onChange={(e) => setBillTitle(e.target.value)}
            placeholder={t("billTitlePlaceholder")}
          />
          <Input type="date" value={billDue} onChange={(e) => setBillDue(e.target.value)} />
          <div className="flex gap-2">
            <Button variant="outline" className="flex-1" onClick={back}>
              {t("back")}
            </Button>
            <Button variant="secondary" className="flex-1" disabled={busy} onClick={() => saveBill(true)}>
              {t("skip")}
            </Button>
          </div>
          <Button className="w-full" disabled={busy || !billTitle || !billDue} onClick={() => saveBill(false)}>
            {t("continue")}
          </Button>
        </section>
      )}

      {step === 5 && (
        <section className="space-y-5">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">{t("cycleTitle")}</h1>
            <p className="mt-2 text-muted-foreground">{t("cycleBody")}</p>
          </div>
          <Button className="w-full" size="lg" disabled={busy} onClick={() => saveCycle(true)}>
            {t("cycleEnable")}
          </Button>
          <Button variant="outline" className="w-full" size="lg" disabled={busy} onClick={() => saveCycle(false)}>
            {t("cycleSkip")}
          </Button>
          <Button variant="ghost" onClick={back}>
            {t("back")}
          </Button>
        </section>
      )}

      {step === 6 && (
        <section className="space-y-5">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">{t("doneTitle")}</h1>
            <p className="mt-3 text-muted-foreground leading-relaxed">{t("doneBody")}</p>
          </div>
          <Button className="w-full" size="lg" disabled={busy} onClick={finish}>
            {t("finish")}
          </Button>
        </section>
      )}
    </div>
  );
}
