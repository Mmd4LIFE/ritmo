"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useLocale } from "@/components/locale-provider";

const links = [
  { href: "/digest", key: "digest" },
  { href: "/calendar", key: "calendar" },
  { href: "/cycle", key: "cycle" },
  { href: "/profile", key: "profile" },
] as const;

export default function MorePage() {
  const t = useTranslations("more");
  const { dir } = useLocale();
  const Chevron = dir === "rtl" ? ChevronLeft : ChevronRight;

  return (
    <div className="page space-y-4">
      <h1 className="text-2xl font-semibold">{t("title")}</h1>
      <div className="overflow-hidden rounded-xl border border-border bg-card">
        {links.map((item, idx) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center justify-between px-4 py-4 text-sm font-medium ${
              idx ? "border-t border-border" : ""
            }`}
          >
            <span>{t(item.key)}</span>
            <Chevron className="h-4 w-4 text-muted-foreground" />
          </Link>
        ))}
      </div>
    </div>
  );
}
