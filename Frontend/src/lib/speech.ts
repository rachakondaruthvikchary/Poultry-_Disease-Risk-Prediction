import { LANGUAGE_VOICE, Language } from "@/lib/translations";

let cachedVoices: SpeechSynthesisVoice[] = [];

type SpeechCallbacks = {
  onStart?: () => void;
  onEnd?: () => void;
  onError?: () => void;
};

export type SpeechPlaybackHandle = {
  mode: "speech" | "audio";
  cancel: () => void;
};

const LANGUAGE_HINTS: Record<Language, string[]> = {
  en: ["english", "en-us", "en-gb", "us", "uk"],
  hi: ["hindi", "india", "indic", "hi-in", "devanagari"],
  te: ["telugu", "india", "indic", "te-in", "andhra", "dravidian"],
};

function getVoiceCandidates(lang: Language): string[] {
  const locale = LANGUAGE_VOICE[lang];
  const base = locale.split("-")[0];
  return [locale.toLowerCase(), base.toLowerCase(), ...LANGUAGE_HINTS[lang]];
}

function scoreVoice(voice: SpeechSynthesisVoice, lang: Language): number {
  const locale = LANGUAGE_VOICE[lang].toLowerCase();
  const base = locale.split("-")[0];
  const voiceLang = voice.lang.toLowerCase();
  const searchable = `${voice.name} ${voice.voiceURI} ${voice.lang}`.toLowerCase();

  if (voiceLang === locale) return 100;
  if (voiceLang.startsWith(`${base}-`)) return 90;
  if (voiceLang === base) return 80;

  const hintIndex = LANGUAGE_HINTS[lang].findIndex((hint) => searchable.includes(hint));
  if (hintIndex >= 0) {
    return 70 - hintIndex;
  }

  if (voiceLang.includes(base)) return 60;

  return -1;
}

function setCachedVoices(voices: SpeechSynthesisVoice[]) {
  if (voices.length > 0) {
    cachedVoices = voices;
  }
}

function getAvailableVoices(): SpeechSynthesisVoice[] {
  const synth = window.speechSynthesis;
  const existingVoices = synth.getVoices();
  setCachedVoices(existingVoices);
  return cachedVoices;
}

export function primeSpeechVoices(timeoutMs = 1500): void {
  if (!("speechSynthesis" in window)) {
    return;
  }

  const synth = window.speechSynthesis;
  setCachedVoices(synth.getVoices());

  const previousHandler = synth.onvoiceschanged;
  synth.onvoiceschanged = (event) => {
    setCachedVoices(synth.getVoices());
    previousHandler?.call(synth, event ?? new Event("voiceschanged"));
  };

  window.setTimeout(() => {
    setCachedVoices(synth.getVoices());
  }, timeoutMs);
}

export function resolveSpeechVoice(lang: Language): SpeechSynthesisVoice | null {
  const voices = getAvailableVoices();
  const candidates = getVoiceCandidates(lang);

  return voices
    .map((voice) => ({
      voice,
      score: Math.max(
        scoreVoice(voice, lang),
        candidates.findIndex((candidate) =>
          `${voice.name} ${voice.voiceURI} ${voice.lang}`.toLowerCase().includes(candidate)
        ) >= 0
          ? 55
          : -1
      ),
    }))
    .filter((entry) => entry.score >= 0)
    .sort((left, right) => right.score - left.score)[0]?.voice ?? null;
}

function splitMessageForAudio(message: string, maxLength = 170): string[] {
  const compact = message.replace(/\s+/g, " ").trim();
  if (!compact) {
    return [];
  }

  const chunks: string[] = [];
  let remaining = compact;

  while (remaining.length > maxLength) {
    const boundary = Math.max(
      remaining.lastIndexOf(". ", maxLength),
      remaining.lastIndexOf("! ", maxLength),
      remaining.lastIndexOf("? ", maxLength),
      remaining.lastIndexOf("। ", maxLength),
      remaining.lastIndexOf(".\n", maxLength)
    );

    const splitAt = boundary > 0 ? boundary + 1 : remaining.lastIndexOf(" ", maxLength);
    const safeIndex = splitAt > 0 ? splitAt : maxLength;

    chunks.push(remaining.slice(0, safeIndex).trim());
    remaining = remaining.slice(safeIndex).trim();
  }

  if (remaining) {
    chunks.push(remaining);
  }

  return chunks;
}

function buildFallbackAudioUrls(message: string, lang: Language): string[] {
  const locale = LANGUAGE_VOICE[lang].split("-")[0].toLowerCase();

  // Prefer backend TTS proxy (more reliable and avoids CORS/rate-limit issues).
  // Backend runs on port 8000 by default in this repo.
  const host = typeof window !== "undefined" ? window.location.hostname : "localhost";
  const protocol = typeof window !== "undefined" ? window.location.protocol : "http:";
  const backendBase = `${protocol}//${host}:8000/api`;

  return splitMessageForAudio(message).map((chunk) => `${backendBase}/tts?lang=${locale}&text=${encodeURIComponent(chunk)}`);
}

function playAudioFallback(message: string, lang: Language, callbacks: SpeechCallbacks): SpeechPlaybackHandle | null {
  if (typeof Audio === "undefined") {
    return null;
  }

  const urls = buildFallbackAudioUrls(message, lang);
  if (urls.length === 0) {
    return null;
  }

  let cancelled = false;
  let currentAudio: HTMLAudioElement | null = null;
  let currentIndex = 0;
  let started = false;

  const cleanup = () => {
    if (currentAudio) {
      currentAudio.onended = null;
      currentAudio.onerror = null;
      currentAudio.pause();
      currentAudio.src = "";
      currentAudio = null;
    }
  };

  const playNext = () => {
    if (cancelled) {
      cleanup();
      return;
    }

    if (currentIndex >= urls.length) {
      cleanup();
      callbacks.onEnd?.();
      return;
    }

    const audio = new Audio(urls[currentIndex]);
    audio.preload = "auto";
    currentAudio = audio;

    audio.onended = () => {
      currentIndex += 1;
      playNext();
    };

    audio.onerror = () => {
      cleanup();
      callbacks.onError?.();
    };

    if (!started) {
      started = true;
      callbacks.onStart?.();
    }

    void audio.play().catch(() => {
      cleanup();
      callbacks.onError?.();
    });
  };

  playNext();

  return {
    mode: "audio",
    cancel: () => {
      cancelled = true;
      cleanup();
      callbacks.onEnd?.();
    },
  };
}

export function speakWithBestAvailableVoice(
  message: string,
  lang: Language,
  rate = 0.9,
  pitch = 1,
  callbacks: SpeechCallbacks = {}
): SpeechPlaybackHandle | null {
  const canUseSpeechSynthesis = typeof window !== "undefined" && "speechSynthesis" in window;
  const forceBackend =
    typeof window !== "undefined" && (window.localStorage?.getItem("pg_force_backend_tts") === "1");
  const matchingVoice = canUseSpeechSynthesis ? resolveSpeechVoice(lang) : null;

  // Prefer backend audio for Hindi or when the user forced backend TTS.
  if (lang === "hi" || forceBackend) {
    const fallbackHandle = playAudioFallback(message, lang, callbacks);
    if (fallbackHandle) return fallbackHandle;
    // if fallback failed, continue to attempt browser TTS below
  }

  // If the browser supports SpeechSynthesis, attempt to use it.
  if (canUseSpeechSynthesis) {
    const utterance = new SpeechSynthesisUtterance(message);
    utterance.lang = LANGUAGE_VOICE[lang];
    utterance.rate = rate;
    utterance.pitch = pitch;

    if (matchingVoice) {
      utterance.voice = matchingVoice;
    }

    // Debug: log the voice selection so developers can see what was used.
    try {
      // eslint-disable-next-line no-console
      console.debug("speakWithBestAvailableVoice: using speechSynthesis", {
        requestedLang: LANGUAGE_VOICE[lang],
        selectedVoice: matchingVoice ? matchingVoice.name : null,
        voiceLang: utterance.lang,
      });
    } catch (e) {
      // ignore
    }

    utterance.onstart = () => callbacks.onStart?.();
    utterance.onend = () => callbacks.onEnd?.();
    utterance.onerror = () => callbacks.onError?.();

    window.speechSynthesis.speak(utterance);

    return {
      mode: "speech",
      cancel: () => {
        window.speechSynthesis.cancel();
        callbacks.onEnd?.();
      },
    };
  }

  return playAudioFallback(message, lang, callbacks);
}

export function setForceBackendTTS(enabled: boolean) {
  if (typeof window === "undefined") return;
  try {
    if (enabled) {
      window.localStorage.setItem("pg_force_backend_tts", "1");
    } else {
      window.localStorage.removeItem("pg_force_backend_tts");
    }
  } catch (e) {
    // ignore
  }
}

export function isForceBackendTTS(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return window.localStorage.getItem("pg_force_backend_tts") === "1";
  } catch (e) {
    return false;
  }
}

// Expose a small helper for debugging voices in the console
export function listAvailableVoices(): SpeechSynthesisVoice[] {
  return getAvailableVoices();
}