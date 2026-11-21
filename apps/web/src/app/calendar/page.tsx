"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

export default function CalendarPage() {
  const t = useTranslations("calendar");
  const { token } = useAuth();
  const [events, setEvents] = useState<{ id: string; title: string; starts_at: string; source: string }[]>([]);
  const [title, setTitle] = useState("");
  const [when, setWhen] = useState("");

  const load = async () => {
    if (!token) return;
    setEvents(await api.calendar.list(token));
  };

  useEffect(() => {
    load().catch(console.error);
  }, [token]);

  if (!token) return <div className="page" />;

  return (
    <div className="page space-y-4">
      <h1 className="text-2xl font-semibold">{t("title")}</h1>

      <div className="space-y-2 rounded-xl border border-border bg-card p-3">
        <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Event" />
        <Input type="datetime-local" value={when} onChange={(e) => setWhen(e.target.value)} />
        <Button
          className="w-full"
          onClick={async () => {
            if (!title || !when) return;
            await api.calendar.create(token, {
              title,
              starts_at: new Date(when).toISOString(),
              all_day: false,
            });
            setTitle("");
            setWhen("");
            await load();
          }}
        >
          {t("add")}
        </Button>
      </div>

      <div className="space-y-3">
        {events.length === 0 && <p className="text-sm text-muted-foreground">{t("empty")}</p>}
        {events.map((e) => (
          <Card key={e.id}>
            <CardHeader>
              <CardTitle>{e.title}</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              {new Date(e.starts_at).toLocaleString()} · {e.source}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
