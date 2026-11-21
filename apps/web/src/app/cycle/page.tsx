"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

export default function CyclePage() {
  const t = useTranslations("cycle");
  const { token } = useAuth();
  const [data, setData] = useState<{
    avg_cycle_days: number;
    avg_period_days: number;
    last_start?: string;
    predicted_next?: string;
    reminders_enabled: boolean;
  } | null>(null);
  const [start, setStart] = useState("");

  const load = async () => {
    if (!token) return;
    setData(await api.cycle.get(token));
  };

  useEffect(() => {
    load().catch(console.error);
  }, [token]);

  if (!token) return <div className="page" />;

  return (
    <div className="page space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">{t("title")}</h1>
        <p className="text-sm text-muted-foreground">{t("private")}</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t("predicted")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>
            {t("lastStart")}: {data?.last_start || "—"}
          </p>
          <p>
            {t("predicted")}: {data?.predicted_next || "—"}
          </p>
          <p>
            {t("avgCycle")}: {data?.avg_cycle_days ?? 28}
          </p>
          <p>
            {t("avgPeriod")}: {data?.avg_period_days ?? 5}
          </p>
        </CardContent>
      </Card>

      <div className="space-y-2 rounded-xl border border-border bg-card p-3">
        <Input type="date" value={start} onChange={(e) => setStart(e.target.value)} />
        <Button
          className="w-full"
          onClick={async () => {
            if (!start) return;
            await api.cycle.log(token, start);
            setStart("");
            await load();
          }}
        >
          {t("log")}
        </Button>
        <Button
          variant="outline"
          className="w-full"
          onClick={async () => {
            await api.cycle.patch(token, { reminders_enabled: !data?.reminders_enabled });
            await load();
          }}
        >
          {t("reminders")}: {data?.reminders_enabled ? t("on") : t("off")}
        </Button>
      </div>
    </div>
  );
}
