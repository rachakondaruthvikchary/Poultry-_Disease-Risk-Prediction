"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import {
  Volume2,
  VolumeX,
  Mic,
  MicOff,
  Languages,
  HelpCircle,
  Check,
  ChevronUp,
  ChevronDown,
  AudioLines,
} from "lucide-react";
import { useLanguage } from "@/lib/language-context";
import {
  primeSpeechVoices,
  speakWithBestAvailableVoice,
  type SpeechPlaybackHandle,
  listAvailableVoices,
  setForceBackendTTS,
  isForceBackendTTS,
} from "@/lib/speech";
import { buildVoiceMessage, getLocalizedDiseaseName, LANGUAGE_VOICE, LANGUAGE_NAMES, Language } from "@/lib/translations";

interface VoiceAgentProps {
  risk: string;
  disease: string;
  alertCount: number;
  status: string;
}

interface SpeechRecognitionAlternative {
  transcript: string;
}

interface SpeechRecognitionResultLike {
  isFinal: boolean;
  0: SpeechRecognitionAlternative;
}

interface SpeechRecognitionEventLike extends Event {
  results: ArrayLike<SpeechRecognitionResultLike>;
}

interface SpeechRecognitionErrorEventLike extends Event {
  error: string;
}

interface SpeechRecognitionLike {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onstart: (() => void) | null;
  onend: (() => void) | null;
  onerror: ((event: SpeechRecognitionErrorEventLike) => void) | null;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
}

declare global {
  interface Window {
    SpeechRecognition?: new () => SpeechRecognitionLike;
    webkitSpeechRecognition?: new () => SpeechRecognitionLike;
  }
}

const HELP_MESSAGES: Record<Language, string> = {
  en: "This voice assistant helps you understand your farm's health status. Select your preferred language, then tap Listen and speak naturally. You can ask for risk, disease, alerts, help, or change the language.",
  hi: "यह आवाज़ सहायक आपको अपने फार्म की स्थिति समझने में मदद करता है। अपनी भाषा चुनें, फिर सुनो बटन दबाकर सामान्य रूप से बोलें। आप जोखिम, रोग, अलर्ट, मदद या भाषा बदलने के लिए बोल सकते हैं।",
  te: "ఈ వాయిస్ అసిస్టెంట్ మీ ఫారం స్థితిని అర్థం చేసుకోవడంలో సహాయపడుతుంది. మీ భాషను ఎంచుకుని, విను బటన్ నొక్కి సహజంగా మాట్లాడండి. మీరు ప్రమాదం, వ్యాధి, హెచ్చరికలు, సహాయం లేదా భాష మార్చమని చెప్పవచ్చు.",
};

const UI_TEXT: Record<Language, {
  hideHelp: string;
  needHelp: string;
  playHelp: string;
  listen: string;
  stopListening: string;
  handsFree: string;
  tapCommand: string;
  quickCommands: string;
  listeningNow: string;
  heardYou: string;
  assistantReply: string;
  browserNoSpeech: string;
  browserNoListen: string;
  listeningHint: string;
  tapToOpen: string;
  ttsLabel: string;
  ttsUseServer: string;
  ttsUseBrowser: string;
}> = {
  en: {
    hideHelp: "Hide Help",
    needHelp: "Need Help?",
    playHelp: "Play Help Audio",
    listen: "Listen to Me",
    stopListening: "Stop Listening",
    handsFree: "Hands-Free Mode",
    tapCommand: "Tap a command",
    quickCommands: "Quick Commands",
    listeningNow: "Listening now... speak clearly",
    heardYou: "Heard You",
    assistantReply: "Assistant Reply",
    browserNoSpeech: "Your browser does not support speech. Please use Chrome or Edge.",
    browserNoListen: "Your browser does not support voice listening. Please use Chrome or Edge.",
    listeningHint: "Try: tell me farm status, alerts, disease, help, switch to Hindi or Telugu.",
    tapToOpen: "Tap to Talk",
    ttsLabel: "TTS Mode",
    ttsUseServer: "Use Server TTS",
    ttsUseBrowser: "Use Browser TTS",
  },
  hi: {
    hideHelp: "मदद छुपाएँ",
    needHelp: "मदद चाहिए?",
    playHelp: "मदद ऑडियो चलाएँ",
    listen: "मेरी आवाज़ सुनो",
    stopListening: "सुनना बंद करें",
    handsFree: "हैंड्स-फ्री मोड",
    tapCommand: "किसी कमांड पर दबाएँ",
    quickCommands: "त्वरित कमांड",
    listeningNow: "सुन रहा हूँ... साफ़ बोलें",
    heardYou: "आपने कहा",
    assistantReply: "सहायक का जवाब",
    browserNoSpeech: "आपका ब्राउज़र स्पीच सपोर्ट नहीं करता। कृपया Chrome या Edge उपयोग करें।",
    browserNoListen: "आपका ब्राउज़र आवाज़ सुनने का सपोर्ट नहीं करता। कृपया Chrome या Edge उपयोग करें।",
    listeningHint: "ऐसे बोलें: फार्म स्थिति बताओ, अलर्ट बताओ, बीमारी बताओ, मदद, हिंदी या तेलुगु में बदलो।",
    tapToOpen: "बात करने के लिए दबाएँ",
    ttsLabel: "TTS मोड",
    ttsUseServer: "सर्वर TTS उपयोग करें",
    ttsUseBrowser: "ब्राउज़र TTS उपयोग करें",
  },
  te: {
    hideHelp: "సహాయం దాచు",
    needHelp: "సహాయం కావాలా?",
    playHelp: "సహాయం ఆడియో ప్లే చేయి",
    listen: "నా మాట విను",
    stopListening: "వినడం ఆపు",
    handsFree: "హ్యాండ్స్-ఫ్రీ మోడ్",
    tapCommand: "కమాండ్‌ని నొక్కండి",
    quickCommands: "త్వరిత కమాండ్లు",
    listeningNow: "వింటున్నాను... స్పష్టంగా మాట్లాడండి",
    heardYou: "మీరు చెప్పింది",
    assistantReply: "అసిస్టెంట్ సమాధానం",
    browserNoSpeech: "మీ బ్రౌజర్ స్పీచ్‌ను సపోర్ట్ చేయదు. దయచేసి Chrome లేదా Edge వాడండి.",
    browserNoListen: "మీ బ్రౌజర్ వాయిస్ లిసనింగ్‌ను సపోర్ట్ చేయదు. దయచేసి Chrome లేదా Edge వాడండి.",
    listeningHint: "ఇలా చెప్పండి: ఫారం స్థితి చెప్పు, హెచ్చరికలు చెప్పు, వ్యాధి చెప్పు, సహాయం, హిందీ లేదా తెలుగు మార్చు.",
    tapToOpen: "మాట్లాడటానికి నొక్కండి",
    ttsLabel: "TTS మోడ్",
    ttsUseServer: "సర్వర్ TTS ఉపయోగించు",
    ttsUseBrowser: "బ్రౌజర్ TTS ఉపయోగించు",
  },
};

function detectRequestedLanguage(text: string): Language | null {
  const lower = text.toLowerCase();
  if (/(english|inglish)/.test(lower)) return "en";
  if (/(hindi|hindii|हिंदी|हिन्दी)/.test(lower)) return "hi";
  if (/(telugu|telgu|తెలుగు)/.test(lower)) return "te";
  return null;
}

function buildQuickReply(lang: Language, text: string, risk: string, disease: string, alertCount: number, status: string) {
  const lower = text.toLowerCase();
  const requestedLanguage = detectRequestedLanguage(text);

  if (/(stop listening|stop|quit listening|listen off|వినడం ఆపు|ఆపు|सुनना बंद|बंद करो)/.test(lower)) {
    if (lang === "hi") {
      return { reply: "ठीक है, मैं सुनना बंद कर रहा हूँ।", nextLanguage: null };
    }
    if (lang === "te") {
      return { reply: "సరే, నేను వినడం ఆపుతున్నాను.", nextLanguage: null };
    }
    return { reply: "Okay, I am stopping listening.", nextLanguage: null };
  }

  if (requestedLanguage) {
    if (requestedLanguage === "hi") {
      return {
        reply:
          lang === "hi"
            ? "भाषा हिंदी में बदल दी गई है। अब आप मुझसे फार्म स्थिति, अलर्ट या बीमारी के बारे में पूछ सकते हैं।"
            : requestedLanguage === "hi"
              ? "भाषा हिंदी में बदल दी गई है।"
              : "Language changed to Hindi.",
        nextLanguage: requestedLanguage,
      };
    }
    if (requestedLanguage === "te") {
      return {
        reply:
          requestedLanguage === "te"
            ? "భాషను తెలుగుకు మార్చాను. ఇప్పుడు మీరు ఫారం స్థితి, హెచ్చరికలు లేదా వ్యాధి గురించి అడగవచ్చు."
            : "Language changed to Telugu.",
        nextLanguage: requestedLanguage,
      };
    }
    return {
      reply:
        requestedLanguage === "en"
          ? "Language changed to English. You can now ask about risk, disease, alerts, or help."
          : "Language changed to English.",
      nextLanguage: requestedLanguage,
    };
  }

  if (/(help|assist|how to use|मदद|सहायता|సహాయం)/.test(lower)) {
    return { reply: HELP_MESSAGES[lang], nextLanguage: null };
  }

  if (/(alert|alerts|अलर्ट|चेतावनी|హెచ్చరిక)/.test(lower)) {
    if (lang === "hi") {
      return { reply: `आपके फार्म में अभी ${alertCount} अलर्ट हैं।`, nextLanguage: null };
    }
    if (lang === "te") {
      return { reply: `మీ ఫారంలో ప్రస్తుతం ${alertCount} హెచ్చరికలు ఉన్నాయి.`, nextLanguage: null };
    }
    return { reply: `Your farm currently has ${alertCount} alerts.`, nextLanguage: null };
  }

  if (/(disease|prediction|रोग|बीमारी|వ్యాధి)/.test(lower)) {
    if (lang === "hi") {
      return { reply: `नवीनतम रोग पूर्वानुमान ${getLocalizedDiseaseName(lang, disease)} है।`, nextLanguage: null };
    }
    if (lang === "te") {
      return { reply: `తాజా వ్యాధి అంచనా ${getLocalizedDiseaseName(lang, disease)}.`, nextLanguage: null };
    }
    return { reply: `The latest disease prediction is ${getLocalizedDiseaseName(lang, disease)}.`, nextLanguage: null };
  }

  if (/(risk|status|farm|स्थिति|जोखिम|फार्म|స్థితి|ప్రమాదం|ఫారం)/.test(lower)) {
    return { reply: buildVoiceMessage(lang, risk, disease, alertCount, status), nextLanguage: null };
  }

  if (lang === "hi") {
    return {
      reply: "मैं आपकी मदद के लिए तैयार हूँ। आप बोल सकते हैं: फार्म स्थिति बताओ, अलर्ट बताओ, बीमारी बताओ, मदद, या भाषा बदलो।",
      nextLanguage: null,
    };
  }
  if (lang === "te") {
    return {
      reply: "నేను సహాయం చేయడానికి సిద్ధంగా ఉన్నాను. మీరు ఇలా చెప్పవచ్చు: ఫారం స్థితి చెప్పు, హెచ్చరికలు చెప్పు, వ్యాధి చెప్పు, సహాయం, లేదా భాష మార్చు.",
      nextLanguage: null,
    };
  }
  return {
    reply: "I am ready to help. You can say: tell me farm status, alerts, disease, help, or change language.",
    nextLanguage: null,
  };
}

function getCommandSuggestions(lang: Language) {
  if (lang === "hi") {
    return ["फार्म स्थिति", "अलर्ट", "बीमारी", "मदद", "हिंदी", "तेलुगु"];
  }
  if (lang === "te") {
    return ["ఫారం స్థితి", "హెచ్చరికలు", "వ్యాధి", "సహాయం", "హిందీ", "తెలుగు"];
  }
  return ["Farm Status", "Alerts", "Disease", "Help", "Hindi", "Telugu"];
}

export function VoiceAgent({ risk, disease, alertCount, status }: VoiceAgentProps) {
  const { lang, setLang, t } = useLanguage();
  const [forceBackendTts, setForceBackendTts] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [listening, setListening] = useState(false);
  const [handsFree, setHandsFree] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [showLangSelector, setShowLangSelector] = useState(true);
  const [lastMessage, setLastMessage] = useState("");
  const [heardText, setHeardText] = useState("");
  const [assistantReply, setAssistantReply] = useState("");
  const playbackRef = useRef<SpeechPlaybackHandle | null>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const shouldRestartListeningRef = useRef(false);

  useEffect(() => {
    primeSpeechVoices();
    setForceBackendTts(isForceBackendTTS());

    return () => {
      window.speechSynthesis?.cancel();
      recognitionRef.current?.abort();
    };
  }, []);

  const speakText = useCallback((message: string, voiceLang: Language = lang, rate = 0.9) => {
    if (!("speechSynthesis" in window) && typeof Audio === "undefined") {
      alert(UI_TEXT[lang].browserNoSpeech);
      return;
    }

    window.speechSynthesis.cancel();
    playbackRef.current?.cancel();
    playbackRef.current = speakWithBestAvailableVoice(message, voiceLang, rate, 1, {
      onStart: () => setSpeaking(true),
      onEnd: () => {
        playbackRef.current = null;
        setSpeaking(false);
        if (shouldRestartListeningRef.current) {
          setTimeout(() => {
            const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!Recognition) return;
            if (!recognitionRef.current && !listening) {
              // restarted by listening flow
            }
          }, 250);
        }
      },
      onError: () => {
        playbackRef.current = null;
        setSpeaking(false);
      },
    });

    if (!playbackRef.current) {
      setSpeaking(false);
      alert(UI_TEXT[lang].browserNoSpeech);
      return;
    }

    setLastMessage(message);
  }, [lang, listening]);

  const speak = useCallback(() => {
    speakText(buildVoiceMessage(lang, risk, disease, alertCount, status));
  }, [alertCount, disease, lang, risk, speakText, status]);

  const stop = () => {
    playbackRef.current?.cancel();
    playbackRef.current = null;
    window.speechSynthesis.cancel();
    recognitionRef.current?.abort();
    setSpeaking(false);
    setListening(false);
  };

  const speakHelp = () => {
    speakText(HELP_MESSAGES[lang], lang, 0.85);
  };

  const changeLanguage = (newLang: Language) => {
    setLang(newLang);
    playbackRef.current?.cancel();
    playbackRef.current = null;
    window.speechSynthesis.cancel();
    recognitionRef.current?.abort();
    setSpeaking(false);
    setListening(false);
  };

  const toggleTtsMode = (useServer?: boolean) => {
    const next = typeof useServer === "boolean" ? useServer : !forceBackendTts;
    setForceBackendTTS(next);
    setForceBackendTts(next);
    // stop any current playback to avoid mixed outputs
    playbackRef.current?.cancel();
    playbackRef.current = null;
    window.speechSynthesis.cancel();
  };

  const startListening = (forceContinuous?: boolean) => {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
      alert(UI_TEXT[lang].browserNoListen);
      return;
    }

    shouldRestartListeningRef.current = forceContinuous ?? handsFree;
    recognitionRef.current?.abort();
    recognitionRef.current = null;
    playbackRef.current?.cancel();
    playbackRef.current = null;
    window.speechSynthesis.cancel();

    const recognition = new Recognition();
    recognition.lang = LANGUAGE_VOICE[lang];
    recognition.continuous = forceContinuous ?? handsFree;
    recognition.interimResults = true;

    recognition.onstart = () => {
      setListening(true);
      setHeardText("");
      setAssistantReply("");
    };

    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = 0; i < event.results.length; i += 1) {
        transcript += event.results[i][0].transcript;
      }

      const cleanTranscript = transcript.trim();
      setHeardText(cleanTranscript);

      const lastResult = event.results[event.results.length - 1];
      if (!lastResult?.isFinal || !cleanTranscript) return;

      const { reply, nextLanguage } = buildQuickReply(lang, cleanTranscript, risk, disease, alertCount, status);
      const replyLanguage = nextLanguage ?? lang;

      if (/(stop listening|stop|quit listening|listen off|వినడం ఆపు|ఆపు|सुनना बंद|बंद करो)/.test(cleanTranscript.toLowerCase())) {
        shouldRestartListeningRef.current = false;
      }

      if (nextLanguage) {
        setLang(nextLanguage);
      }

      setAssistantReply(reply);
      setLastMessage(reply);
      speakText(reply, replyLanguage, 0.92);
    };

    recognition.onerror = () => {
      setListening(false);
      recognitionRef.current = null;
      if (lang === "hi") {
        setAssistantReply("मैं आपकी आवाज़ साफ़ सुन नहीं पाया। कृपया फिर से कोशिश करें।");
      } else if (lang === "te") {
        setAssistantReply("మీ మాట స్పష్టంగా వినలేకపోయాను. దయచేసి మళ్లీ ప్రయత్నించండి.");
      } else {
        setAssistantReply("I could not hear you clearly. Please try again.");
      }
    };

    recognition.onend = () => {
      setListening(false);
      recognitionRef.current = null;
      if (shouldRestartListeningRef.current) {
        setTimeout(() => {
          if (!window.speechSynthesis.speaking) {
            startListening(true);
          }
        }, 500);
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    shouldRestartListeningRef.current = false;
    recognitionRef.current?.stop();
    recognitionRef.current = null;
    setListening(false);
  };

  const runCommandChip = (command: string) => {
    setHeardText(command);
    const { reply, nextLanguage } = buildQuickReply(lang, command, risk, disease, alertCount, status);
    const replyLanguage = nextLanguage ?? lang;
    if (nextLanguage) {
      setLang(nextLanguage);
    }
    setAssistantReply(reply);
    speakText(reply, replyLanguage, 0.92);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
      {expanded && (
        <div className="glass soft-noise panel-entrance border border-amber-600/20 dark:border-amber-500/35 rounded-[2rem] shadow-2xl p-6 w-[26rem] text-sm max-h-[32rem] overflow-y-auto">
          <div className="flex items-center justify-between gap-2 mb-4">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 bg-gradient-to-br from-red-600 via-red-600 to-red-700 rounded-[1.35rem] grid place-items-center text-white shrink-0 shadow-lg">
                {listening ? <AudioLines className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </div>
              <div className="flex-1">
                <p className="font-display font-semibold tracking-[-0.03em] text-slate-900 dark:text-white text-2xl">{t("voiceAgent")}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {listening ? UI_TEXT[lang].listeningNow : t("voiceAgentDesc")}
                </p>
              </div>
            </div>
            <button
              onClick={() => setExpanded(false)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition"
            >
              <ChevronDown className="w-5 h-5" />
            </button>
          </div>

          <div className="mb-4 p-4 rounded-[1.6rem] border border-emerald-200 dark:border-emerald-900 bg-emerald-50/70 dark:bg-emerald-950/20">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="font-semibold text-slate-800 dark:text-slate-100">{UI_TEXT[lang].handsFree}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">{UI_TEXT[lang].listeningHint}</p>
              </div>
              <button
                onClick={() => {
                  const next = !handsFree;
                  setHandsFree(next);
                  shouldRestartListeningRef.current = next && listening;
                }}
                className={`relative h-7 w-14 rounded-full transition ${handsFree ? "bg-emerald-500" : "bg-slate-300 dark:bg-slate-600"}`}
                aria-label={UI_TEXT[lang].handsFree}
              >
                <span
                  className={`absolute top-1 h-5 w-5 rounded-full bg-white transition ${handsFree ? "left-8" : "left-1"}`}
                />
              </button>
            </div>
            <div className="mt-3 flex items-center justify-between">
              <div className="text-xs text-slate-600 dark:text-slate-300 font-semibold">{UI_TEXT[lang].ttsLabel}</div>
              <div className="flex gap-2">
                <button
                  onClick={() => toggleTtsMode(true)}
                  className={`px-3 py-2 rounded-xl text-xs font-bold ${forceBackendTts ? "bg-red-600 text-white" : "bg-white/85 text-slate-700"}`}
                >
                  {UI_TEXT[lang].ttsUseServer}
                </button>
                <button
                  onClick={() => toggleTtsMode(false)}
                  className={`px-3 py-2 rounded-xl text-xs font-bold ${!forceBackendTts ? "bg-red-600 text-white" : "bg-white/85 text-slate-700"}`}
                >
                  {UI_TEXT[lang].ttsUseBrowser}
                </button>
              </div>
            </div>
          </div>

          <div className="mb-4 p-4 rounded-[1.6rem] border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-900/40">
            <p className="text-xs font-bold text-slate-500 dark:text-slate-400 mb-3 uppercase tracking-wide">{UI_TEXT[lang].quickCommands}</p>
            <div className="flex flex-wrap gap-2">
              {getCommandSuggestions(lang).map((command) => (
                <button
                  key={command}
                  onClick={() => runCommandChip(command)}
                  className="px-3 py-2 rounded-full bg-white/85 dark:bg-slate-800 hover:-translate-y-0.5 hover:bg-red-50 dark:hover:bg-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 transition"
                >
                  {command}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4 p-4 bg-gradient-to-r from-teal-50 to-amber-50 dark:from-slate-700/50 dark:to-slate-800/50 rounded-[1.6rem] border border-teal-200/50 dark:border-teal-900/30">
            <button
              onClick={() => setShowLangSelector((value) => !value)}
              className="flex items-center justify-between w-full mb-3"
            >
              <div className="flex items-center gap-2">
                <Languages className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <h3 className="font-bold text-slate-700 dark:text-slate-200">{t("selectLanguage")}</h3>
              </div>
              <ChevronUp className={`w-4 h-4 transition-transform ${showLangSelector ? "rotate-180" : ""}`} />
            </button>

            {showLangSelector && (
              <div className="grid grid-cols-3 gap-2">
                {(["en", "hi", "te"] as Language[]).map((language) => (
                  <button
                    key={language}
                    onClick={() => changeLanguage(language)}
                    className={`relative px-3 py-3 rounded-xl text-sm font-bold transition-all transform ${
                      lang === language
                        ? "bg-gradient-to-br from-red-600 to-red-700 text-white shadow-lg scale-105"
                        : "bg-white/85 dark:bg-slate-600 text-slate-600 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-500 border border-slate-200 dark:border-slate-500"
                    }`}
                  >
                    {LANGUAGE_NAMES[language]}
                    {lang === language && (
                      <Check className="w-4 h-4 absolute top-1 right-1 bg-white rounded-full text-red-600 p-0.5" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="mb-4">
            <button
              onClick={() => setShowHelp((value) => !value)}
              className="flex items-center justify-between w-full text-teal-700 dark:text-teal-300 hover:text-teal-800 dark:hover:text-teal-200 py-3 px-4 bg-teal-50 dark:bg-teal-900/20 rounded-2xl transition"
            >
              <div className="flex items-center gap-2">
                <HelpCircle className="w-4 h-4" />
                <span className="font-semibold">{showHelp ? UI_TEXT[lang].hideHelp : UI_TEXT[lang].needHelp}</span>
              </div>
              <ChevronUp className={`w-4 h-4 transition-transform ${showHelp ? "rotate-180" : ""}`} />
            </button>

            {showHelp && (
              <div className="mt-2 p-4 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800/50 rounded-[1.6rem]">
                <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed mb-3 font-medium">
                  {HELP_MESSAGES[lang]}
                </p>
                <button
                  onClick={speakHelp}
                  className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2.5 rounded-xl text-xs font-bold w-full justify-center transition shadow-md"
                >
                  <Volume2 className="w-4 h-4" />
                  {UI_TEXT[lang].playHelp}
                </button>
              </div>
            )}
          </div>

          {heardText && (
            <div className="mb-3 p-4 bg-sky-50 dark:bg-sky-950/30 rounded-[1.6rem] border border-sky-200 dark:border-sky-900">
              <p className="text-xs font-bold text-sky-700 dark:text-sky-300 mb-2 uppercase tracking-wide">
                🎙️ {UI_TEXT[lang].heardYou}
              </p>
              <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">{heardText}</p>
            </div>
          )}

          {assistantReply && (
            <div className="mb-3 p-4 bg-teal-50 dark:bg-teal-950/30 rounded-[1.6rem] border border-teal-200 dark:border-teal-900">
              <p className="text-xs font-bold text-violet-700 dark:text-violet-300 mb-2 uppercase tracking-wide">
                🤖 {UI_TEXT[lang].assistantReply}
              </p>
              <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">{assistantReply}</p>
            </div>
          )}

          {lastMessage && (
            <div className="mb-4 p-4 bg-gradient-to-r from-slate-50 to-stone-100 dark:from-slate-900 dark:to-slate-800 rounded-[1.6rem] border border-slate-200 dark:border-slate-700">
              <p className="text-xs font-bold text-slate-500 dark:text-slate-400 mb-2 uppercase tracking-wide">{(UI_TEXT[lang] as any).lastMessageLabel || "📢 Last Message"}</p>
              <p className="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">{lastMessage}</p>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {speaking ? (
              <button
                onClick={stop}
                className="flex items-center gap-2 bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white px-5 py-3 rounded-2xl text-sm font-bold w-full justify-center transition shadow-lg transform hover:scale-[1.02]"
              >
                <VolumeX className="w-5 h-5" />
                {t("stopSpeaking")}
              </button>
            ) : (
              <button
                onClick={speak}
                className="flex items-center gap-2 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white px-5 py-3 rounded-2xl text-sm font-bold w-full justify-center transition shadow-lg transform hover:scale-[1.02]"
              >
                <Volume2 className="w-5 h-5" />
                {t("speak")}
              </button>
            )}

            {listening ? (
              <button
                onClick={stopListening}
                className="flex items-center gap-2 bg-gradient-to-r from-rose-500 to-pink-600 hover:from-rose-600 hover:to-pink-700 text-white px-5 py-3 rounded-xl text-sm font-bold w-full justify-center transition shadow-lg transform hover:scale-[1.02]"
              >
                <MicOff className="w-5 h-5" />
                {UI_TEXT[lang].stopListening}
              </button>
            ) : (
              <button
                onClick={() => startListening()}
                className="flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white px-5 py-3 rounded-2xl text-sm font-bold w-full justify-center transition shadow-lg transform hover:scale-[1.02]"
              >
                <Mic className="w-5 h-5" />
                {UI_TEXT[lang].listen}
              </button>
            )}
          </div>
        </div>
      )}

      <button
        onClick={() => setExpanded((value) => !value)}
        className={`relative w-16 h-16 rounded-[1.75rem] shadow-2xl flex items-center justify-center transition-all transform hover:scale-110 active:scale-95 ${
          listening
            ? "bg-gradient-to-br from-emerald-500 to-teal-600 animate-pulse shadow-emerald-500/50"
            : speaking
              ? "bg-gradient-to-br from-red-500 to-rose-600 animate-pulse shadow-red-500/50"
              : expanded
                ? "bg-gradient-to-br from-red-600 to-red-700 shadow-lg"
                : "bg-gradient-to-br from-red-600 to-red-700 hover:shadow-lg"
        } text-white font-bold text-lg`}
        title={t("voiceAgent")}
      >
        {listening ? <AudioLines className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
        {expanded && (
          <div className={`absolute -top-2 -right-2 w-4 h-4 rounded-full animate-pulse border-2 border-white ${listening ? "bg-emerald-500" : "bg-green-500"}`} />
        )}
        {!expanded && (
          <div className="absolute bottom-1 right-1 text-xs bg-red-600/80 dark:bg-red-500/80 px-1.5 py-0.5 rounded-full text-white font-semibold">
            {lang.toUpperCase()}
          </div>
        )}
      </button>

      {!expanded && (
        <div className="text-xs font-semibold text-slate-700 dark:text-slate-200 bg-white/90 dark:bg-slate-800 px-3 py-2 rounded-2xl shadow-md border border-slate-200 dark:border-slate-700 backdrop-blur-md">
          {t("voiceAgent")} - {UI_TEXT[lang].tapToOpen}
        </div>
      )}
    </div>
  );
}
