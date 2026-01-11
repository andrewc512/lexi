import Link from "next/link";
import { SUPPORTED_LANGUAGES } from "@/types/language";

const LANGUAGE_FLAGS: Record<string, string> = {
  en: "🇺🇸",
  es: "🇪🇸",
  fr: "🇫🇷",
  de: "🇩🇪",
  zh: "🇨🇳",
  ja: "🇯🇵",
};

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation Header */}
      <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
        <nav className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            </div>
            <span className="text-2xl font-semibold text-gray-900">Lexi</span>
          </div>

          {/* Auth Buttons */}
          <div className="flex items-center space-x-4">
            <Link
              href="/login"
              className="text-gray-700 hover:text-gray-900 transition-colors font-medium"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium whitespace-nowrap"
            >
              Register →
            </Link>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12 md:py-20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left Section - Content */}
          <div className="space-y-8">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 leading-tight">
              Can you speak...
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              Are you a recruiter trying to gauge language proficiency? Lexi conducts AI-powered language assessment interviews to evaluate language fluency for your candidates.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
              <Link
                href="/register"
                className="bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition-colors font-semibold text-lg inline-flex items-center group"
              >
                Start Interviewing
                <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
              </Link>
            </div>
          </div>

          {/* Right Section - Visual Element */}
          <div className="relative">
            <div className="relative bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-8 shadow-xl">
              {/* Interview Interface Mockup */}
              <div className="bg-white rounded-xl p-6 shadow-lg space-y-4">
                <div className="flex items-center justify-between border-b pb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-semibold">JD</span>
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900">Interview in Progress</div>
                      <div className="text-sm text-gray-500">Question 2 of 5</div>
                    </div>
                  </div>
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                </div>
                
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-gray-700 mb-3">Tell me about a time when you had to work under a tight deadline.</p>
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span>Recording...</span>
                    </div>
                  </div>
                  
                  <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
                    <div className="text-xs text-blue-600 font-medium mb-1">AI Analysis</div>
                    <p className="text-sm text-gray-700">
                      Candidate demonstrates strong problem-solving skills and clear communication.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Decorative elements */}
            <div className="absolute -top-4 -right-4 w-24 h-24 bg-blue-200 rounded-full opacity-20 blur-2xl"></div>
            <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-purple-200 rounded-full opacity-20 blur-2xl"></div>
          </div>
        </div>

        {/* Languages Supported */}
        <div className="mt-24 pt-16 pb-16 border-t border-gray-200">
          <div className="text-center space-y-6">
            <h2 className="text-3xl md:text-4xl text-gray-900">Languages Supported</h2>
            <div className="flex flex-wrap justify-center items-center gap-x-6 gap-y-3 text-lg text-gray-700">
              {SUPPORTED_LANGUAGES.map((lang, index) => (
                <span key={lang.code} className="font-medium flex items-center gap-2">
                  <span className="text-2xl">{LANGUAGE_FLAGS[lang.code]}</span>
                  {lang.name}
                  {index < SUPPORTED_LANGUAGES.length - 1 && (
                    <span className="mx-3 text-gray-400">•</span>
                  )}
                </span>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
