"use client";

interface ReadingPassageProps {
  passage: string;
  language: string;
  difficulty: number;
  instruction: string;
}

export function ReadingPassage({ passage, language, difficulty, instruction }: ReadingPassageProps) {
  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg border-2 border-blue-500">
      {/* Header */}
      <div className="mb-4 pb-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-semibold text-gray-900">Reading Exercise</h2>
          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
            Level {difficulty}
          </span>
        </div>
        <p className="text-sm text-gray-600">{instruction}</p>
      </div>

      {/* Passage */}
      <div className="mb-4">
        <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
          {language} Text
        </div>
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-lg leading-relaxed text-gray-900" lang={language}>
            {passage}
          </p>
        </div>
      </div>

      {/* Translation instruction */}
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
        <span>Speak your English translation when ready</span>
      </div>
    </div>
  );
}
