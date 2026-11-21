"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

export default function BillsPage() {
  const t = useTranslations("bills");
  const { token } = useAuth();
  const [bills, setBills] = useState<
    { id: string; title: string; amount?: string; currency: string; next_due: string; warn_days: number }[]
  >([]);
  const [title, setTitle] = useState("");
  const [due, setDue] = useState("");
  const [amount, setAmount] = useState("");

  const load = async () => {
    if (!token) return;
    setBills(await api.bills.list(token));
  };

  useEffect(() => {
    load().catch(console.error);
  }, [token]);

  if (!token) return <div className="page" />;

  return (
    <div className="page space-y-4">
      <h1 className="text-2xl font-semibold">{t("title")}</h1>

      <div className="space-y-2 rounded-xl border border-border bg-card p-3">
        <Input placeholder="Rent / Internet / Phone" value={title} onChange={(e) => setTitle(e.target.value)} />
        <Input type="date" value={due} onChange={(e) => setDue(e.target.value)} />
        <Input
          placeholder={t("amount")}
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          inputMode="decimal"
        />
        <Button
          className="w-full"
          onClick={async () => {
            if (!title || !due) return;
            await api.bills.create(token, {
              title,
              next_due: due,
              amount: amount ? Number(amount) : null,
              currency: "IRR",
              warn_days: 3,
              recurrence: "monthly",
            });
            setTitle("");
            setDue("");
            setAmount("");
            await load();
          }}
        >
          {t("add")}
        </Button>
      </div>

      <div className="space-y-3">
        {bills.map((b) => (
          <Card key={b.id}>
            <CardHeader>
              <CardTitle>{b.title}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>{t("due", { date: b.next_due })}</p>
              <p className="text-muted-foreground">{t("warn", { n: b.warn_days })}</p>
              {b.amount && (
                <p>
                  {b.amount} {b.currency}
                </p>
              )}
              <Button
                variant="secondary"
                className="w-full"
                onClick={async () => {
                  await api.bills.paid(token, b.id);
                  await load();
                }}
              >
                {t("paid")}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
