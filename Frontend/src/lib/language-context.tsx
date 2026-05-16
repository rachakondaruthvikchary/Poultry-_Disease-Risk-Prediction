"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { Language, TranslationKey, t as _t } from "@/lib/translations";

interface LanguageContextType {
  lang: Language;
  setLang: (l: Language) => void;
  t: (key: TranslationKey) => string;
}

const LanguageContext = createContext<LanguageContextType>({
  lang: "en",
  setLang: () => {},
  t: (key) => key,
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  // Default the app to Hindi so the voice assistant speaks Hindi by default.
  const [lang, setLangState] = useState<Language>("hi");

  useEffect(() => {
    const saved = localStorage.getItem("pg_language") as Language | null;
    if (saved && ["en", "hi", "te"].includes(saved)) setLangState(saved);
    // Force backend TTS by default for reliable Hindi audio unless user overrides
    try {
      if (!localStorage.getItem("pg_force_backend_tts")) {
        localStorage.setItem("pg_force_backend_tts", "1");
      }
    } catch (e) {
      // ignore storage errors
    }
  }, []);

  const setLang = (l: Language) => {
    setLangState(l);
    localStorage.setItem("pg_language", l);
  };

  const t = (key: TranslationKey) => _t(lang, key);

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
