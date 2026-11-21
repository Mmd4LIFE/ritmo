"use client";

import { useAuth } from "@/components/auth-provider";
import { BottomNav } from "@/components/nav";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const showNav = !loading && !!user?.onboarding_done;

  return (
    <>
      <main>{children}</main>
      {showNav ? <BottomNav /> : null}
    </>
  );
}
