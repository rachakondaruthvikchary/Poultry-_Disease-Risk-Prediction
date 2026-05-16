"use client";

import { useLanguage } from "@/lib/language-context";
import { LANGUAGE_NAMES, Language } from "@/lib/translations";
import { Globe } from "lucide-react";
import { useState, useRef, useEffect } from "react";

const LANGUAGES: Language[] = ["en", "hi", "te"];

export function LanguageSwitcher() {
  const { lang, setLang } = useLanguage();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-haspopup="menu"
        className="flex items-center gap-2 w-full px-3.5 py-3 rounded-[1.15rem] text-sm bg-white/70 dark:bg-slate-900/50 border border-slate-200/80 dark:border-slate-700 hover:-translate-y-0.5 hover:bg-white dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 transition-all shadow-sm"
      >
        <Globe className="h-4 w-4 text-red-600 dark:text-red-400 shrink-0" />
        <span className="font-medium">{LANGUAGE_NAMES[lang]}</span>
        <span className="ml-auto text-xs text-slate-400">▾</span>
      </button>

      {open && (
        <div className="absolute bottom-full left-0 mb-2 w-full bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl border border-slate-200 dark:border-slate-700 rounded-[1.15rem] shadow-xl overflow-hidden z-50" role="menu">
          {LANGUAGES.map((l) => (
            <button
              key={l}
              onClick={() => { setLang(l); setOpen(false); }}
              role="menuitem"
              aria-current={lang === l ? "true" : undefined}
              type="button"
              onKeyDown={(e) => {
                if (e.key === "Escape") setOpen(false);
                if (e.key === "ArrowDown" || e.key === "ArrowUp") e.preventDefault();
                if (e.key === "Enter" || e.key === " ") { setLang(l); setOpen(false); }
              }}
              className={`flex items-center gap-2 w-full px-3.5 py-3 text-sm transition-colors ${
                lang === l
                  ? "bg-gradient-to-r from-red-600 to-red-700 text-white dark:from-red-600 dark:to-red-700"
                  : "hover:bg-red-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200"
              }`}
            >
              {lang === l && <span className="text-xs">✓</span>}
              {lang !== l && <span className="text-xs opacity-0">✓</span>}
              {LANGUAGE_NAMES[l]}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
