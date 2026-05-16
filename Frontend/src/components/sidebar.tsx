"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { LayoutDashboard, FileSearch, History, ClipboardPenLine } from "lucide-react";
import { useLanguage } from "@/lib/language-context";
import { LanguageSwitcher } from "@/components/language-switcher";
import { TranslationKey } from "@/lib/translations";

type NavItem = { href: string; labelKey: TranslationKey; icon: React.ElementType };

const items: NavItem[] = [
  { href: "/dashboard",                  labelKey: "navOverview",       icon: LayoutDashboard },
  { href: "/dashboard/farm-data",        labelKey: "navFarmData",       icon: ClipboardPenLine },
  { href: "/dashboard/image-detection",  labelKey: "navImageDetection", icon: FileSearch },
  { href: "/dashboard/history",          labelKey: "navHistory",        icon: History },
];

export function Sidebar() {
  const pathname = usePathname();
  const { t } = useLanguage();

  return (
    <aside className="glass soft-noise w-full lg:w-72 rounded-[2rem] p-4 h-fit lg:sticky lg:top-6 overflow-hidden">
      <div className="flex items-center gap-3 px-2 py-3">
        <div className="h-11 w-11 rounded-[1.25rem] bg-gradient-to-br from-red-600 via-red-600 to-red-700 text-white grid place-items-center shadow-lg">
          <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a1 1 0 011 1v1.323l3.954 1.115a1 1 0 11-.547 1.929L11 5.823v5.354l3.954 1.116a1 1 0 11-.547 1.929L11 12.677v2a1 1 0 11-2 0v-2.323L5.046 14.68a1 1 0 11.547-1.929L9 12.677V7.323L5.046 6.207a1 1 0 11.547-1.929L9 5.323V3a1 1 0 011-1h1zm-6 8a1 1 0 10-2 0 1 1 0 002 0zm12 0a1 1 0 10-2 0 1 1 0 002 0z" />
          </svg>
        </div>
        <div>
          <p className="font-display text-lg font-semibold tracking-[-0.02em] text-red-900">{t("appName")}</p>
          <p className="text-xs uppercase tracking-[0.18em] text-red-700 dark:text-red-400">{t("appSubtitle")}</p>
        </div>
      </div>

      {/* Language switcher — always visible below logo */}
      <div className="mt-2 mb-1 px-1">
        <LanguageSwitcher />
      </div>

      <nav className="mt-3 space-y-2">
        {items.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 rounded-[1.25rem] px-3.5 py-3 text-sm transition-all duration-200",
                active
                  ? "bg-gradient-to-r from-red-600 to-red-700 text-white shadow-lg"
                  : "bg-white/45 dark:bg-slate-900/25 text-red-900 dark:text-red-100 hover:-translate-y-0.5 hover:bg-red-50/70 dark:hover:bg-red-900/40"
              )}
            >
              <Icon className="h-4 w-4" />
              {t(item.labelKey)}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
