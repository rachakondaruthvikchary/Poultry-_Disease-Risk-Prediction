"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Globe, Volume2, VolumeX, Mic } from "lucide-react";
import { useLanguage } from "@/lib/language-context";
import { primeSpeechVoices, speakWithBestAvailableVoice, type SpeechPlaybackHandle } from "@/lib/speech";
import { LANGUAGE_NAMES, Language, buildVoiceMessage } from "@/lib/translations";

interface LanguageVoicePanelProps {
  risk?: string;
  disease?: string;
  alertCount?: number;
  status?: string;
}

const LANGUAGES: Language[] = ["en", "hi", "te"];

export function LanguageVoicePanel({
  risk = "Low",
  disease = "No prediction",
  alertCount = 0,
  status = "Stable",
}: LanguageVoicePanelProps) {
  const { lang, setLang, t } = useLanguage();
  const [speaking, setSpeaking] = useState(false);
  const [lastMsg, setLastMsg] = useState("");
  const playbackRef = useRef<SpeechPlaybackHandle | null>(null);

  useEffect(() => {
    primeSpeechVoices();
  }, []);

  const speak = useCallback(() => {
    if (!("speechSynthesis" in window) && typeof Audio === "undefined") {
      alert("Your browser does not support speech. Please use Chrome or Edge.");
      return;
    }

    playbackRef.current?.cancel();
    window.speechSynthesis.cancel();
    const message = buildVoiceMessage(lang, risk, disease, alertCount, status);
    setLastMsg(message);
    playbackRef.current = speakWithBestAvailableVoice(message, lang, 0.88, 1, {
      onStart: () => setSpeaking(true),
      onEnd: () => {
        playbackRef.current = null;
        setSpeaking(false);
      },
      onError: () => {
        playbackRef.current = null;
        setSpeaking(false);
      },
    });
  }, [lang, risk, disease, alertCount, status]);

  const stop = () => {
    playbackRef.current?.cancel();
    playbackRef.current = null;
    window.speechSynthesis.cancel();
    setSpeaking(false);
  };

  return (
    <div className="glass soft-noise rounded-[2rem] p-5 md:p-6 overflow-hidden panel-entrance">
      <div className="flex flex-col sm:flex-row gap-5">

        {/* ── Language Section ── */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-red-500/30 to-red-200 text-red-600 dark:text-red-400 dark:from-red-600/40 dark:to-red-500/30 grid place-items-center">
              <Globe className="w-4 h-4" />
            </div>
            <div>
              <p className="font-display text-xl font-semibold tracking-[-0.03em]">{t("selectLanguage")}</p>
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Choose your preferred language</p>
            </div>
          </div>
          <div className="flex gap-2">
            {LANGUAGES.map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={`flex-1 py-3 px-3 rounded-2xl text-sm font-semibold transition-all border ${
                  lang === l
                    ? "bg-gradient-to-br from-red-600 to-red-700 text-white border-red-500 shadow-lg"
                    : "border-slate-200/80 dark:border-slate-700 text-slate-600 dark:text-slate-300 bg-white/60 dark:bg-slate-900/35 hover:-translate-y-0.5 hover:bg-white dark:hover:bg-slate-800"
                }`}
              >
                {LANGUAGE_NAMES[l]}
              </button>
            ))}
          </div>
        </div>

        {/* Divider */}
        <div className="hidden sm:block w-px bg-slate-200 dark:bg-slate-700" />
        <div className="block sm:hidden h-px bg-slate-200 dark:bg-slate-700" />

        {/* ── Voice Section ── */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-3">
            <div className={`w-9 h-9 rounded-2xl grid place-items-center ${speaking ? "bg-red-100 dark:bg-red-900/30 text-red-600" : "bg-gradient-to-br from-red-500/30 to-red-200 text-red-600 dark:text-red-400 dark:from-red-600/40 dark:to-red-500/30"}`}>
              <Mic className="w-4 h-4" />
            </div>
            <div>
              <p className="font-display text-xl font-semibold tracking-[-0.03em]">{t("voiceAgent")}</p>
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{t("voiceAgentDesc")}</p>
            </div>
          </div>

          {/* Last spoken message preview */}
          {lastMsg && (
            <p className="text-xs text-slate-600 dark:text-slate-300 bg-white/70 dark:bg-slate-800/70 rounded-2xl px-4 py-3 mb-3 leading-relaxed line-clamp-2 border border-slate-200/70 dark:border-slate-700/70">
              {lastMsg}
            </p>
          )}

          <div className="flex gap-2">
            {speaking ? (
              <button
                onClick={stop}
                className="flex items-center justify-center gap-2 bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white px-4 py-3 rounded-2xl text-sm font-semibold w-full transition shadow-lg"
              >
                <VolumeX className="w-4 h-4" />
                {t("stopSpeaking")}
              </button>
            ) : (
              <button
                onClick={speak}
                className="flex items-center justify-center gap-2 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-4 py-3 rounded-2xl text-sm font-semibold w-full transition shadow-lg"
              >
                <Volume2 className="w-4 h-4" />
                {t("speak")}
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
