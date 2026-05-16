"use client";

import { Sidebar } from "@/components/sidebar";
import { DashboardVoiceAgent } from "@/components/dashboard-voice-agent";
import { ThemeToggle } from "@/components/theme-toggle";
import { clearToken, loadToken } from "@/lib/auth";
import { useLanguage } from "@/lib/language-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { t } = useLanguage();

  useEffect(() => {
    const token = loadToken();
    if (!token) router.push("/login");
  }, [router]);

  return (
    <main className="relative p-4 lg:p-6">
      <div className="mx-auto max-w-7xl grid grid-cols-1 lg:grid-cols-[18rem_1fr] gap-4 lg:gap-6">
        <Sidebar />
        <section className="space-y-4">
          <header className="glass soft-noise rounded-[2rem] px-5 py-5 md:px-6 md:py-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between panel-entrance overflow-hidden">
            <div className="relative z-10">
              <p className="text-[0.7rem] uppercase tracking-[0.32em] text-red-700 dark:text-red-400 font-bold">🐔 Poultry Intelligence</p>
              <h1 className="font-display mt-1 text-2xl md:text-3xl font-bold tracking-tight text-red-900 dark:text-red-50">{t("consoleTitle")}</h1>
              <p className="mt-2 max-w-2xl text-sm md:text-[0.95rem] text-red-800 dark:text-red-200">{t("consoleSubtitle")}</p>
            </div>
            <div className="relative z-10 flex items-center gap-2 self-start md:self-auto">
              <ThemeToggle />
              <button
                className="rounded-2xl border border-red-300/70 dark:border-red-700 bg-red-50/70 dark:bg-red-900/40 px-4 py-2.5 text-sm font-medium text-red-900 dark:text-red-100 shadow-sm transition hover:-translate-y-0.5 hover:border-red-500/60"
                onClick={() => {
                  clearToken();
                  router.push("/login");
                }}
              >
                {t("logout")}
              </button>
            </div>
          </header>
          {children}
        </section>
      </div>
      <DashboardVoiceAgent />
    </main>
  );
}
