"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

type Habit = {
  id: string;
  kind: string;
  title: string;
  emoji?: string;
  streak_current: number;
  checked_today: boolean;
};

const PRESETS = [
  { kind: "water", emoji: "💧" },
  { kind: "study", emoji: "📚" },
  { kind: "gym", emoji: "🏋️" },
  { kind: "no_smoking", emoji: "🚭" },
] as const;

export default function HabitsPage() {
  const t = useTranslations("habits");
  const { token } = useAuth();
  const [habits, setHabits] = useState<Habit[]>([]);
  const [title, setTitle] = useState("");

  const load = async () => {
    if (!token) return;
    setHabits(await api.habits.list(token));
  };

  useEffect(() => {
    load().catch(console.error);
  }, [token]);

  if (!token) return <div className="page" />;

  return (
    <div className="page space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">{t("title")}</h1>
        <p className="mt-1 text-sm text-muted-foreground">{t("hint")}</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {PRESETS.map((p) => (
          <Button
            key={p.kind}
            size="sm"
            variant="outline"
            onClick={async () => {
              await api.habits.create(token, {
                kind: p.kind,
                title: t(`kinds.${p.kind}`),
                emoji: p.emoji,
              });
              await load();
            }}
          >
            {p.emoji} {t(`kinds.${p.kind}`)}
          </Button>
        ))}
      </div>

      <div className="flex gap-2">
        <Input
          placeholder={t("kinds.custom")}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <Button
          onClick={async () => {
            if (!title.trim()) return;
            await api.habits.create(token, { kind: "custom", title: title.trim() });
            setTitle("");
            await load();
          }}
        >
          {t("add")}
        </Button>
      </div>

      {habits.length === 0 && <p className="text-sm text-muted-foreground">{t("empty")}</p>}

      <div className="space-y-3">
        {habits.map((h) => (
          <Card key={h.id}>
            <CardHeader className="flex-row items-center justify-between space-y-0">
              <CardTitle>
                {h.emoji ? `${h.emoji} ` : ""}
                {h.title}
              </CardTitle>
              <span className="text-sm text-muted-foreground">{t("streak", { n: h.streak_current })}</span>
            </CardHeader>
            <CardContent>
              {h.checked_today ? (
                <p className="text-sm text-primary">{t("checked")}</p>
              ) : (
                <Button
                  className="w-full"
                  onClick={async () => {
                    await api.habits.checkin(token, h.id);
                    await load();
                  }}
                >
                  {t("checkin")}
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
