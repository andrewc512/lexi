"use client";

import { useState, useRef, useEffect } from "react";
import { supabase } from "@/lib/supabaseClient";
import { SUPPORTED_LANGUAGES, SupportedLanguage } from "@/types/language";
import { API_BASE_URL } from "@/lib/constants";

interface CandidateFormProps {
  onInterviewCreated?: () => void;
}

export function CandidateForm({ onInterviewCreated }: CandidateFormProps) {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [language, setLanguage] = useState<SupportedLanguage>("en");
  const [searchInput, setSearchInput] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const searchContainerRef = useRef<HTMLDivElement>(null);

  // Filter languages based on search input
  const filteredLanguages = SUPPORTED_LANGUAGES.filter(
    (lang) =>
      lang.name.toLowerCase().includes(searchInput.toLowerCase()) ||
      lang.nativeName.toLowerCase().includes(searchInput.toLowerCase()) ||
      lang.code.toLowerCase().includes(searchInput.toLowerCase())
  );

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        searchContainerRef.current &&
        !searchContainerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelectLanguage = (selectedLang: SupportedLanguage) => {
    setLanguage(selectedLang);
    const selectedLangObj = SUPPORTED_LANGUAGES.find(
      (lang) => lang.code === selectedLang
    );
    if (selectedLangObj) {
      setSearchInput(`${selectedLangObj.name} (${selectedLangObj.nativeName})`);
    }
    setIsOpen(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    setLoadingMessage("Creating interview...");

    try {
      // Get the current authenticated user
      const {
        data: { user },
        error: userError,
      } = await supabase.auth.getUser();

      if (userError || !user) {
        throw new Error("You must be logged in to create an interview");
      }

      console.log("Submitting interview:", { email, name, language });
      
      // Step 1: Insert into Supabase
      const { data, error: insertError } = await supabase
        .from("interviews")
        .insert([
          {
            email: email,
            name: name,
            language: language,
            status: "pending",
            user_id: user.id,
          },
        ])
        .select()
        .single();

      if (insertError) {
        console.error("Supabase error:", insertError);
        throw new Error(insertError.message || "Failed to create interview");
      }

      console.log("Interview created successfully:", data);
      
      // Step 2: Send invitation email
      setLoadingMessage("Sending invitation email...");
      
      const emailResponse = await fetch(`${API_BASE_URL}/email/send-invite`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          interview_id: data.id,
          candidate_email: email,
          candidate_name: name,
          language: getLanguageName(language),
        }),
      });

      if (!emailResponse.ok) {
        const errorData = await emailResponse.json().catch(() => ({}));
        console.warn("Email sending failed:", errorData);
        // Don't throw - interview was created, just warn about email
        setSuccess(`Interview created! Note: Email could not be sent automatically.`);
      } else {
        setSuccess(`Interview created and invitation sent to ${email}!`);
      }

      // Reset form
      setEmail("");
      setName("");
      setLanguage("en");
      setSearchInput("");
      setError(null);

      // Notify parent to refresh the interview list
      if (onInterviewCreated) {
        onInterviewCreated();
      }
    } catch (error: any) {
      console.error("Failed to create interview:", error);
      setError(error?.message || "Failed to create interview. Please try again.");
    } finally {
      setLoading(false);
      setLoadingMessage("");
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">New Candidate</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            placeholder="Candidate name"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            placeholder="candidate@example.com"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Language
          </label>
          <div ref={searchContainerRef} className="relative">
            <input
              type="text"
              value={searchInput}
              onChange={(e) => {
                setSearchInput(e.target.value);
                setIsOpen(true);
              }}
              onFocus={() => setIsOpen(true)}
              placeholder="Search languages..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
            {isOpen && filteredLanguages.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-48 overflow-y-auto">
                {filteredLanguages.map((lang) => (
                  <button
                    key={lang.code}
                    type="button"
                    onClick={() => handleSelectLanguage(lang.code)}
                    className={`w-full text-left px-3 py-2 hover:bg-blue-50 ${
                      language === lang.code ? "bg-blue-100" : ""
                    }`}
                  >
                    <div className="font-medium">{lang.name}</div>
                    <div className="text-sm text-gray-500">
                      {lang.nativeName}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
            {error}
          </div>
        )}
        
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md text-sm">
            {success}
          </div>
        )}
        
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              {loadingMessage}
            </span>
          ) : (
            "Create Interview & Send Email"
          )}
        </button>
      </form>
    </div>
  );
}
