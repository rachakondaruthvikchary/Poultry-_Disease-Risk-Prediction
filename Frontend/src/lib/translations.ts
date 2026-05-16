export type Language = "en" | "hi" | "te";

export const LANGUAGE_NAMES: Record<Language, string> = {
  en: "English",
  hi: "हिंदी",
  te: "తెలుగు",
};

export const LANGUAGE_VOICE: Record<Language, string> = {
  en: "en-US",
  hi: "hi-IN",
  te: "te-IN",
};

function normalizeKey(value: string): string {
  return value
    .toLowerCase()
    .replace(/[()]/g, "")
    .replace(/[\/_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

const DISEASE_TRANSLATIONS: Record<string, Record<Language, string>> = {
  "No prediction": {
    en: "No prediction yet",
    hi: "अभी तक कोई पूर्वानुमान नहीं",
    te: "ఇంకా అంచనా లేదు",
  },
  Healthy: {
    en: "Healthy",
    hi: "स्वस्थ",
    te: "ఆరోగ్యంగా ఉంది",
  },
  "Newcastle disease": {
    en: "Newcastle disease",
    hi: "न्यूकैसल रोग",
    te: "న్యూ క్యాసిల్ వ్యాధి",
  },
  "Avian Influenza": {
    en: "Avian Influenza",
    hi: "एवियन इन्फ्लुएंजा",
    te: "ఏవియన్ ఇన్ ఫ్లూయెంజా",
  },
  Coccidiosis: {
    en: "Coccidiosis",
    hi: "कॉक्सिडियोसिस",
    te: "కాక్సిడియోసిస్",
  },
  "Infectious Bursal Disease": {
    en: "Infectious Bursal Disease",
    hi: "संक्रामक बर्सल रोग",
    te: "ఇన్ఫెక్షియస్ బర్సల్ డిసీజ్",
  },
  "Infectious Bronchitis": {
    en: "Infectious Bronchitis",
    hi: "संक्रामक ब्रोंकाइटिस",
    te: "ఇన్ఫెక్షియస్ బ్రాంకైటిస్",
  },
  "Marek's Disease": {
    en: "Marek's Disease",
    hi: "मारेक रोग",
    te: "మారెక్ వ్యాధి",
  },
  "Fowl Pox": {
    en: "Fowl Pox",
    hi: "फाउल पॉक्स",
    te: "ఫౌల్ పాక్స్",
  },
  "Fowl Cholera": {
    en: "Fowl Cholera",
    hi: "फाउल कॉलरा",
    te: "ఫౌల్ కాలెరా",
  },
  "Mycoplasmosis (CRD)": {
    en: "Mycoplasmosis",
    hi: "माइकोप्लाज़्मोसिस",
    te: "మైకోప్లాస్మోసిస్",
  },
  "Infectious Coryza": {
    en: "Infectious Coryza",
    hi: "संक्रामक कोराइज़ा",
    te: "ఇన్ఫెక్షియస్ కోరైజా",
  },
  "Salmonellosis/Pullorum": {
    en: "Salmonellosis Pullorum",
    hi: "साल्मोनेलोसिस पुलोरम",
    te: "సాల్మోనెల్లోసిస్ పుల్లోరమ్",
  },
};

export type TranslationKey =
  | "appName"
  | "appSubtitle"
  | "consoleTitle"
  | "consoleSubtitle"
  | "navOverview"
  | "navFarmData"
  | "navImageDetection"
  | "navHistory"
  | "currentRisk"
  | "latestPrediction"
  | "totalAlerts"
  | "farmStatus"
  | "riskLow"
  | "riskMedium"
  | "riskHigh"
  | "riskCritical"
  | "statusStable"
  | "statusWarning"
  | "statusCritical"
  | "noPrediction"
  | "speak"
  | "speaking"
  | "stopSpeaking"
  | "selectLanguage"
  | "voiceAgent"
  | "voiceAgentDesc"
  | "authLanguageLabel"
  | "loginTitle"
  | "loginSubtitle"
  | "email"
  | "password"
  | "signIn"
  | "signingIn"
  | "register"
  | "noAccount"
  | "haveAccount"
  | "createAccount"
  | "creatingAccount"
  | "registerTitle"
  | "registerSubtitle"
  | "fullName"
  | "passwordHint"
  | "logout"
  | "farmHealth"
  | "dailyHealthCheck"
  | "saveData"
  | "recordDate"
  | "temperature"
  | "humidity"
  | "feedGiven"
  | "waterUsed"
  | "activityLevel"
  | "deathRate"
  | "birdAge"
  | "savedRecords"
  | "farmerInfo"
  | "riskTrend"
  | "recentAlerts"
  | "noAlerts"
  | "uploadImage"
  | "diseaseDetection"
  | "alertHistory"
  | "language";

const translations: Record<Language, Record<TranslationKey, string>> = {
  en: {
    appName: "PoultryGuard AI",
    appSubtitle: "Disease Early Warning",
    consoleTitle: "Farm Intelligence Console",
    consoleSubtitle: "Real-time disease monitoring and risk analytics",
    navOverview: "Overview",
    navFarmData: "Farm Data",
    navImageDetection: "Image Detection",
    navHistory: "History",
    currentRisk: "Current Risk",
    latestPrediction: "Latest Prediction",
    totalAlerts: "Total Alerts",
    farmStatus: "Farm Status",
    riskLow: "Low",
    riskMedium: "Medium",
    riskHigh: "High",
    riskCritical: "Critical",
    statusStable: "Stable",
    statusWarning: "Warning",
    statusCritical: "Critical",
    noPrediction: "No prediction yet",
    speak: "Speak Status",
    speaking: "Speaking...",
    stopSpeaking: "Stop",
    selectLanguage: "Select Language",
    voiceAgent: "Voice Assistant",
    voiceAgentDesc: "Tap to hear your farm status aloud",
    authLanguageLabel: "App Language",
    loginTitle: "Welcome Back",
    loginSubtitle: "Sign in to monitor flock health and disease alerts",
    email: "Email",
    password: "Password",
    signIn: "Sign In",
    signingIn: "Signing in...",
    register: "Register",
    noAccount: "Don't have an account?",
    haveAccount: "Already have an account?",
    createAccount: "Create Account",
    creatingAccount: "Creating account...",
    registerTitle: "Create Account",
    registerSubtitle: "Join PoultryGuard AI and start monitoring your farm",
    fullName: "Full Name",
    passwordHint: "Minimum 8 characters",
    logout: "Logout",
    farmHealth: "Farm Health",
    dailyHealthCheck: "Daily Farm Health Check",
    saveData: "Save Data & Check Risk",
    recordDate: "Record Date",
    temperature: "Shed Temperature (°C)",
    humidity: "Shed Humidity (%)",
    feedGiven: "Total Feed Given (kg)",
    waterUsed: "Total Water Used (L)",
    activityLevel: "Bird Activity Level (%)",
    deathRate: "Bird Death Rate (%)",
    birdAge: "Average Bird Age (days)",
    savedRecords: "Saved Farm Data Records",
    farmerInfo: "Farmer & Farm Information",
    riskTrend: "14-Day Risk Trend",
    recentAlerts: "Recent Alerts",
    noAlerts: "No alerts yet",
    uploadImage: "Upload Image",
    diseaseDetection: "Disease Detection",
    alertHistory: "Alert History",
    language: "Language",
  },

  hi: {
    appName: "पोल्ट्री गार्ड AI",
    appSubtitle: "रोग प्रारंभिक चेतावनी",
    consoleTitle: "फार्म इंटेलिजेंस कंसोल",
    consoleSubtitle: "रियल-टाइम रोग निगरानी और जोखिम विश्लेषण",
    navOverview: "अवलोकन",
    navFarmData: "फार्म डेटा",
    navImageDetection: "रोग पहचान",
    navHistory: "इतिहास",
    currentRisk: "वर्तमान जोखिम",
    latestPrediction: "नवीनतम पूर्वानुमान",
    totalAlerts: "कुल अलर्ट",
    farmStatus: "फार्म स्थिति",
    riskLow: "कम",
    riskMedium: "मध्यम",
    riskHigh: "उच्च",
    riskCritical: "गंभीर",
    statusStable: "स्थिर",
    statusWarning: "चेतावनी",
    statusCritical: "गंभीर",
    noPrediction: "अभी तक कोई पूर्वानुमान नहीं",
    speak: "स्थिति सुनें",
    speaking: "बोल रहा हूँ...",
    stopSpeaking: "रोकें",
    selectLanguage: "भाषा चुनें",
    voiceAgent: "आवाज़ सहायक",
    voiceAgentDesc: "अपने फार्म की स्थिति सुनने के लिए दबाएं",
    authLanguageLabel: "ऐप भाषा",
    loginTitle: "फिर से स्वागत है",
    loginSubtitle: "अपने झुंड के स्वास्थ्य और रोग अलर्ट देखने के लिए साइन इन करें",
    email: "ईमेल",
    password: "पासवर्ड",
    signIn: "साइन इन",
    signingIn: "साइन इन हो रहा है...",
    register: "रजिस्टर करें",
    noAccount: "क्या आपका खाता नहीं है?",
    haveAccount: "क्या आपका पहले से खाता है?",
    createAccount: "खाता बनाएं",
    creatingAccount: "खाता बनाया जा रहा है...",
    registerTitle: "खाता बनाएं",
    registerSubtitle: "पोल्ट्री गार्ड AI से जुड़ें और अपने फार्म की निगरानी शुरू करें",
    fullName: "पूरा नाम",
    passwordHint: "कम से कम 8 अक्षर",
    logout: "लॉगआउट",
    farmHealth: "फार्म स्वास्थ्य",
    dailyHealthCheck: "दैनिक फार्म स्वास्थ्य जाँच",
    saveData: "डेटा सहेजें और जोखिम जांचें",
    recordDate: "रिकॉर्ड तारीख",
    temperature: "शेड तापमान (°C)",
    humidity: "शेड आर्द्रता (%)",
    feedGiven: "कुल दाना दिया (किलो)",
    waterUsed: "कुल पानी उपयोग (लीटर)",
    activityLevel: "पक्षी गतिविधि स्तर (%)",
    deathRate: "पक्षी मृत्यु दर (%)",
    birdAge: "औसत पक्षी आयु (दिन)",
    savedRecords: "सहेजे गए फार्म डेटा रिकॉर्ड",
    farmerInfo: "किसान और फार्म जानकारी",
    riskTrend: "14-दिन जोखिम रुझान",
    recentAlerts: "हाल के अलर्ट",
    noAlerts: "अभी तक कोई अलर्ट नहीं",
    uploadImage: "तस्वीर अपलोड करें",
    diseaseDetection: "रोग पहचान",
    alertHistory: "अलर्ट इतिहास",
    language: "भाषा",
  },

  te: {
    appName: "పౌల్ట్రీ గార్డ్ AI",
    appSubtitle: "వ్యాధి ముందస్తు హెచ్చరిక",
    consoleTitle: "ఫారం ఇంటెలిజెన్స్ కన్సోల్",
    consoleSubtitle: "రియల్-టైమ్ వ్యాధి పర్యవేక్షణ మరియు ప్రమాద విశ్లేషణ",
    navOverview: "అవలోకనం",
    navFarmData: "వ్యవసాయ డేటా",
    navImageDetection: "వ్యాధి గుర్తింపు",
    navHistory: "చరిత్ర",
    currentRisk: "ప్రస్తుత ప్రమాదం",
    latestPrediction: "తాజా అంచనా",
    totalAlerts: "మొత్తం హెచ్చరికలు",
    farmStatus: "వ్యవసాయ స్థితి",
    riskLow: "తక్కువ",
    riskMedium: "మధ్యమ",
    riskHigh: "అధిక",
    riskCritical: "క్లిష్టమైన",
    statusStable: "స్థిరంగా",
    statusWarning: "హెచ్చరిక",
    statusCritical: "క్లిష్టమైన",
    noPrediction: "ఇంకా అంచనా లేదు",
    speak: "స్థితి వినండి",
    speaking: "మాట్లాడుతున్నాను...",
    stopSpeaking: "ఆపు",
    selectLanguage: "భాష ఎంచుకోండి",
    voiceAgent: "వాయిస్ అసిస్టెంట్",
    voiceAgentDesc: "మీ ఫారం స్థితి వినడానికి నొక్కండి",
    authLanguageLabel: "యాప్ భాష",
    loginTitle: "మళ్లీ స్వాగతం",
    loginSubtitle: "మీ ఫ్లాక్ ఆరోగ్యం మరియు వ్యాధి హెచ్చరికలను చూడడానికి సైన్ ఇన్ చేయండి",
    email: "ఈమెయిల్",
    password: "పాస్‌వర్డ్",
    signIn: "సైన్ ఇన్",
    signingIn: "సైన్ ఇన్ అవుతోంది...",
    register: "రిజిస్టర్",
    noAccount: "ఖాతా లేదా?",
    haveAccount: "ఇప్పటికే ఖాతా ఉందా?",
    createAccount: "ఖాతా సృష్టించండి",
    creatingAccount: "ఖాతా సృష్టిస్తోంది...",
    registerTitle: "ఖాతా సృష్టించండి",
    registerSubtitle: "పౌల్ట్రీ గార్డ్ AI లో చేరి మీ ఫారాన్ని పర్యవేక్షించడం ప్రారంభించండి",
    fullName: "పూర్తి పేరు",
    passwordHint: "కనీసం 8 అక్షరాలు",
    logout: "లాగ్ అవుట్",
    farmHealth: "వ్యవసాయ ఆరోగ్యం",
    dailyHealthCheck: "రోజువారీ ఆరోగ్య తనిఖీ",
    saveData: "డేటా సేవ్ చేయండి & ప్రమాదం తనిఖీ",
    recordDate: "రికార్డు తేదీ",
    temperature: "షెడ్ ఉష్ణోగ్రత (°C)",
    humidity: "షెడ్ తేమ (%)",
    feedGiven: "మొత్తం తిండి (కిలో)",
    waterUsed: "మొత్తం నీరు (లీటర్లు)",
    activityLevel: "పక్షి కార్యాచరణ స్థాయి (%)",
    deathRate: "పక్షి మరణ రేటు (%)",
    birdAge: "సగటు పక్షి వయస్సు (రోజులు)",
    savedRecords: "సేవ్ చేసిన వ్యవసాయ డేటా రికార్డులు",
    farmerInfo: "రైతు & వ్యవసాయ సమాచారం",
    riskTrend: "14-రోజుల ప్రమాద ధోరణి",
    recentAlerts: "ఇటీవలి హెచ్చరికలు",
    noAlerts: "ఇంకా హెచ్చరికలు లేవు",
    uploadImage: "చిత్రం అప్‌లోడ్ చేయండి",
    diseaseDetection: "వ్యాధి గుర్తింపు",
    alertHistory: "హెచ్చరిక చరిత్ర",
    language: "భాష",
  },
};

export function t(lang: Language, key: TranslationKey): string {
  return translations[lang][key] ?? translations.en[key] ?? key;
}

export function getLocalizedRiskLabel(lang: Language, risk: string): string {
  const riskMap: Record<string, Record<Language, string>> = {
    low: { en: "Low", hi: "कम", te: "తక్కువ" },
    medium: { en: "Medium", hi: "मध्यम", te: "మధ్యమ" },
    high: { en: "High", hi: "उच्च", te: "అధిక" },
    critical: { en: "Critical", hi: "गंभीर", te: "క్లిష్టమైన" },
  };

  const normalizedRisk = normalizeKey(risk);

  return riskMap[normalizedRisk]?.[lang] ?? risk;
}

export function getLocalizedStatusLabel(lang: Language, status: string): string {
  const statusMap: Record<string, Record<Language, string>> = {
    stable: { en: "Stable", hi: "स्थिर", te: "స్థిరంగా" },
    warning: { en: "Warning", hi: "चेतावनी", te: "హెచ్చరిక" },
    critical: { en: "Critical", hi: "गंभीर", te: "క్లిష్టమైన" },
  };

  const normalizedStatus = normalizeKey(status);

  return statusMap[normalizedStatus]?.[lang] ?? status;
}

export function getLocalizedDiseaseName(lang: Language, disease: string): string {
  if (!disease || normalizeKey(disease) === "no prediction yet" || normalizeKey(disease) === "no prediction") {
    return DISEASE_TRANSLATIONS["No prediction"]?.[lang] ?? t(lang, "noPrediction");
  }

  const directMatch = DISEASE_TRANSLATIONS[disease]?.[lang];
  if (directMatch) {
    return directMatch;
  }

  const normalizedDisease = normalizeKey(disease);
  const matchedKey = Object.keys(DISEASE_TRANSLATIONS).find(
    (candidate) => normalizeKey(candidate) === normalizedDisease
  );

  return (matchedKey ? DISEASE_TRANSLATIONS[matchedKey]?.[lang] : undefined) ?? disease;
}

/** Build a voice announcement sentence */
export function buildVoiceMessage(
  lang: Language,
  risk: string,
  disease: string,
  alertCount: number,
  status: string
): string {
  const riskTxt = getLocalizedRiskLabel(lang, risk);
  const statTxt = getLocalizedStatusLabel(lang, status);
  const diseaseTxt = getLocalizedDiseaseName(lang, disease);
  const alertTxt = String(alertCount);

  if (lang === "hi") {
    return `आपके मुर्गी फार्म का जोखिम स्तर ${riskTxt} है। नवीनतम रोग पूर्वानुमान ${diseaseTxt} है। आपके पास ${alertTxt} अलर्ट हैं। फार्म की स्थिति ${statTxt} है।`;
  }
  if (lang === "te") {
    return `మీ పౌల్ట్రీ ఫారం ప్రమాద స్థాయి ${riskTxt}. తాజా వ్యాధి అంచనా ${diseaseTxt}. మీకు ${alertTxt} హెచ్చరికలు ఉన్నాయి. వ్యవసాయ స్థితి ${statTxt}.`;
  }
  return `Your poultry farm risk level is ${riskTxt}. Latest disease prediction is ${diseaseTxt}. You have ${alertTxt} alerts. Farm status is ${statTxt}.`;
}
