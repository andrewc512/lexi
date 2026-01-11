export type SupportedLanguage = "en" | "zh-cn" | "hi" | "es" | "ar" | "fr" | "bn" | "pt" | "ru" | "ur" | "id" | "de" | "ja" | "pcm" | "ar-eg" | "mr" | "vi" | "te" | "pa" | "wuu" | "ko" | "sw" | "ha" | "ta" | "it";

export interface LanguageConfig {
  code: SupportedLanguage;
  name: string;
  nativeName: string;
}

export const SUPPORTED_LANGUAGES: LanguageConfig[] = [
  { code: "en", name: "English", nativeName: "English" },
  { code: "zh-cn", name: "Mandarin Chinese", nativeName: "普通话" },
  { code: "hi", name: "Hindi", nativeName: "हिन्दी" },
  { code: "es", name: "Spanish", nativeName: "Español" },
  { code: "ar", name: "Modern Standard Arabic", nativeName: "العربية الفصحى" },
  { code: "fr", name: "French", nativeName: "Français" },
  { code: "bn", name: "Bengali", nativeName: "বাংলা" },
  { code: "pt", name: "Portuguese", nativeName: "Português" },
  { code: "ru", name: "Russian", nativeName: "Русский" },
  { code: "ur", name: "Urdu", nativeName: "اردو" },
  { code: "id", name: "Indonesian", nativeName: "Bahasa Indonesia" },
  { code: "de", name: "German", nativeName: "Deutsch" },
  { code: "ja", name: "Japanese", nativeName: "日本語" },
  { code: "pcm", name: "Nigerian Pidgin", nativeName: "Naijá" },
  { code: "ar-eg", name: "Egyptian Arabic", nativeName: "مصرى" },
  { code: "mr", name: "Marathi", nativeName: "मराठी" },
  { code: "vi", name: "Vietnamese", nativeName: "Tiếng Việt" },
  { code: "te", name: "Telugu", nativeName: "తెలుగు" },
  { code: "pa", name: "Western Punjabi", nativeName: "پنجابی" },
  { code: "wuu", name: "Wu Chinese", nativeName: "吴语" },
  { code: "ko", name: "Korean", nativeName: "한국어" },
  { code: "sw", name: "Swahili", nativeName: "Kiswahili" },
  { code: "ha", name: "Hausa", nativeName: "Hausa" },
  { code: "ta", name: "Tamil", nativeName: "தமிழ்" },
  { code: "it", name: "Italian", nativeName: "Italiano" },
];
