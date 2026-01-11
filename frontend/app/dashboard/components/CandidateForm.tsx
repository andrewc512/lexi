"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabaseClient";
import { SUPPORTED_LANGUAGES, SupportedLanguage } from "@/types/language";

interface CandidateFormProps {
  onInterviewCreated?: () => void;
}

export function CandidateForm({ onInterviewCreated }: CandidateFormProps) {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [language, setLanguage] = useState<SupportedLanguage>("en");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Get the current authenticated user
      const { data: { user }, error: userError } = await supabase.auth.getUser();
      
      if (userError || !user) {
        throw new Error("You must be logged in to create an interview");
      }

      console.log("Submitting interview:", { email, name });
      
      // Insert into Supabase - only fields that exist in the table
      // id and created_at are handled by Supabase (uuid primary key, timestamp default)
      const { data, error: insertError } = await supabase
        .from("interviews")
        .insert([
          {
            email: email,
            name: name,
            language: language,
            status: "Email not sent",
            user_id: user.id,
          },
        ])
        .select()
        .single();

      if (insertError) {
        console.error("Supabase error:", insertError);
        console.error("Error details:", {
          message: insertError.message,
          details: insertError.details,
          hint: insertError.hint,
          code: insertError.code,
        });
        const errorMsg = insertError.message || "Unknown error occurred";
        setError(errorMsg);
        throw insertError;
      }

      console.log("Interview created successfully:", data);
      setEmail("");
      setName("");
      setLanguage("en");
      setError(null);
      
      // Notify parent to refresh the interview list
      if (onInterviewCreated) {
        onInterviewCreated();
      }
    } catch (error: any) {
      console.error("Failed to create interview:", error);
      if (!error?.message) {
        setError("Failed to create interview. Please check the console for details.");
      }
    } finally {
      setLoading(false);
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
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value as SupportedLanguage)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            required
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name} ({lang.nativeName})
              </option>
            ))}
          </select>
        </div>
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
            {error}
          </div>
        )}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Creating..." : "Create Interview"}
        </button>
      </form>
    </div>
  );
}
