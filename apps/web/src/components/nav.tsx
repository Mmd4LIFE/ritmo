"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";
import { CalendarDays, Droplets, Home, Newspaper, Receipt, UserRound, HeartPulse } from "lucide-react";
import { cn } from "@/lib/utils";

const items = [
  { href: "/", key: "home", icon: Home },
  { href: "/habits", key: "habits", icon: Droplets },
  { href: "/bills", key: "bills", icon: Receipt },
  { href: "/cycle", key: "cycle", icon: HeartPulse },
  { href: "/calendar", key: "calendar", icon: CalendarDays },
  { href: "/digest", key: "digest", icon: Newspaper },
  { href: "/profile", key: "profile", icon: UserRound },
] as const;

export function BottomNav() {
  const t = useTranslations("nav");
  const pathname = usePathname();

  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-background/95 backdrop-blur">
      <ul className="mx-auto flex max-w-lg items-stretch justify-between gap-0.5 px-1 py-1">
        {items.map(({ href, key, icon: Icon }) => {
          const active = pathname === href;
          return (
            <li key={href} className="flex-1">
              <Link
                href={href}
                className={cn(
                  "flex flex-col items-center gap-0.5 rounded-md px-1 py-2 text-[10px]",
                  active ? "text-primary" : "text-muted-foreground"
                )}
              >
                <Icon className="h-5 w-5" />
                <span>{t(key)}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
