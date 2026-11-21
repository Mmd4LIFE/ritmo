"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

export default function DigestPage() {
  const t = useTranslations("digest");
  const { token } = useAuth();
  const [city, setCity] = useState("");
  const [hour, setHour] = useState("8");
  const [topic, setTopic] = useState("technology");
  const [prices, setPrices] = useState("USD/IRR");
  const [enabled, setEnabled] = useState(true);
  const [preview, setPreview] = useState("");

  useEffect(() => {
    if (!token) return;
    api.digest.prefs(token).then((p) => {
      setCity(String(p.city || ""));
      setHour(String(p.hour ?? 8));
      setTopic(String(p.news_topic || "technology"));
      setPrices(((p.price_symbols as string[]) || ["USD/IRR"]).join(","));
      setEnabled(Boolean(p.enabled));
    });
  }, [token]);

  if (!token) return <div className="page" />;

  return (
    <div className="page space-y-4">
      <h1 className="text-2xl font-semibold">{t("title")}</h1>

      <div className="space-y-2 rounded-xl border border-border bg-card p-3">
        <label className="text-sm">{t("city")}</label>
        <Input value={city} onChange={(e) => setCity(e.target.value)} placeholder="Tehran" />
        <label className="text-sm">{t("hour")}</label>
        <Input type="number" min={0} max={23} value={hour} onChange={(e) => setHour(e.target.value)} />
        <label className="text-sm">{t("topic")}</label>
        <Input value={topic} onChange={(e) => setTopic(e.target.value)} />
        <label className="text-sm">{t("prices")}</label>
        <Input value={prices} onChange={(e) => setPrices(e.target.value)} />
        <Button
          variant="outline"
          onClick={() => setEnabled((v) => !v)}
        >
          {t("enabled")}: {enabled ? "ON" : "OFF"}
        </Button>
        <Button
          className="w-full"
          onClick={async () => {
            await api.digest.patch(token, {
              city,
              hour: Number(hour),
              news_topic: topic,
              price_symbols: prices.split(",").map((s) => s.trim()).filter(Boolean),
              enabled,
            });
          }}
        >
          {t("save")}
        </Button>
        <Button
          variant="secondary"
          className="w-full"
          onClick={async () => {
            const res = await api.digest.preview(token);
            setPreview(res.text);
          }}
        >
          {t("preview")}
        </Button>
      </div>

      {preview && (
        <Card>
          <CardHeader>
            <CardTitle>{t("preview")}</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="whitespace-pre-wrap text-sm">{preview}</pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
