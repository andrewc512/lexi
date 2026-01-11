"use client";

import { useEffect, useState, useCallback } from "react";
import { supabase } from "@/lib/supabaseClient";
import { Interview } from "@/types/interview";
import { api } from "@/lib/api";

interface InterviewTableProps {
  onSelectInterview: (id: string) => void;
  refreshTrigger?: number;
}

interface InterviewRow {
  id: string;
  email: string;
  name: string;
  token?: string;
  status?: string;
  created_at: string;
  completed_at?: string | null;
  language?: string | null;
  num_eval?: number | null;
  summary_eval?: string | null;
}

const getLanguageFlag = (languageCode: string | null | undefined): string => {
  const flagMap: Record<string, string> = {
    en: "🇺🇸",
    es: "🇪🇸",
    fr: "🇫🇷",
    de: "🇩🇪",
    zh: "🇨🇳",
    ja: "🇯🇵",
  };
  return languageCode ? flagMap[languageCode] || "" : "";
};

export function InterviewTable({ onSelectInterview, refreshTrigger }: InterviewTableProps) {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [interviewRows, setInterviewRows] = useState<InterviewRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [sendingEmail, setSendingEmail] = useState<string | null>(null);
  const [deletingInterview, setDeletingInterview] = useState<string | null>(null);

  const fetchInterviews = useCallback(async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from("interviews")
        .select("*")
        .order("created_at", { ascending: false });

      if (error) {
        console.error("Failed to fetch interviews:", error);
        throw error;
      }

      // Store raw rows for display
      setInterviewRows(data || []);

      // Map database rows to Interview type
      const mappedInterviews: Interview[] = (data || []).map((row: InterviewRow) => ({
        id: row.id,
        token: row.token || "",
        candidateName: row.name,
        candidateEmail: row.email,
        status: (row.status || "pending") as Interview["status"],
        createdAt: new Date(row.created_at).toLocaleDateString(),
        completedAt: row.completed_at ? new Date(row.completed_at).toLocaleDateString() : undefined,
      }));

      setInterviews(mappedInterviews);
    } catch (error) {
      console.error("Failed to fetch interviews:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInterviews();
  }, [fetchInterviews, refreshTrigger]);

  const handleSendEmail = async (row: InterviewRow) => {
    setSendingEmail(row.id);
    try {
      await api.sendInterviewEmail(row.id, row.email, row.name);
      alert(`Email sent to ${row.email}`);
    } catch (error) {
      console.error("Failed to send email:", error);
      alert("Failed to send email. Please try again.");
    } finally {
      setSendingEmail(null);
    }
  };

  const handleDelete = async (row: InterviewRow) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete the interview for ${row.name}? This action cannot be undone.`
    );

    if (!confirmed) {
      return;
    }

    setDeletingInterview(row.id);
    try {
      const { error } = await supabase
        .from("interviews")
        .delete()
        .eq("id", row.id);

      if (error) {
        console.error("Failed to delete interview:", error);
        alert("Failed to delete interview. Please try again.");
        throw error;
      }

      // Refresh the interview list
      await fetchInterviews();
    } catch (error) {
      console.error("Failed to delete interview:", error);
    } finally {
      setDeletingInterview(null);
    }
  };

  if (loading) {
    return <div className="bg-white p-6 rounded-lg shadow">Loading...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 pb-4">
        <h2 className="text-xl font-semibold">Interviews</h2>
      </div>
      {interviews.length === 0 ? (
        <div className="p-6 pt-0">
          <p className="text-gray-500">No interviews yet. Create one using the form on the left.</p>
        </div>
      ) : (
        <div className="overflow-x-auto -mx-6 px-6">
          <table className="w-full table-auto" style={{ minWidth: '800px' }}>
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left py-3 px-4 font-medium text-gray-700">Candidate</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700 w-[160px]">Status</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Score</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Date</th>
                <th className="text-left py-3 px-4 font-medium text-gray-700">Actions</th>
                <th className="text-center py-3 px-4 font-medium text-gray-700 w-12"></th>
              </tr>
            </thead>
            <tbody>
              {interviewRows.map((row) => {
                const interview = interviews.find((i) => i.id === row.id);
                return (
                  <tr key={row.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="font-semibold">{row.name}</div>
                      <div className="text-sm text-gray-500">{row.email}</div>
                      <div className="text-sm text-gray-400 mt-0.5 flex items-center gap-1.5">
                        {row.language && getLanguageFlag(row.language) && (
                          <span>{getLanguageFlag(row.language)}</span>
                        )}
                        <span>{row.language || "-"}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 w-[160px]">
                      <span className="px-2 py-1 text-xs rounded bg-gray-100 whitespace-nowrap">
                        {row.status || "pending"}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {row.num_eval !== null && row.num_eval !== undefined ? row.num_eval : "-"}
                    </td>
                    <td className="py-3 px-4">{interview?.createdAt}</td>
                    <td className="py-3 px-4">
                      <div className="flex flex-col gap-2">
                        <button
                          onClick={() => handleSendEmail(row)}
                          disabled={sendingEmail === row.id}
                          className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-600 transition-colors whitespace-nowrap"
                        >
                          {sendingEmail === row.id ? "Sending..." : "Send Email"}
                        </button>
                        <button
                          onClick={() => onSelectInterview(row.id)}
                          className="px-3 py-1.5 bg-gray-200 text-gray-800 text-sm rounded hover:bg-gray-300 transition-colors whitespace-nowrap"
                        >
                          View Report
                        </button>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <button
                        onClick={() => handleDelete(row)}
                        disabled={deletingInterview === row.id}
                        className="p-1.5 text-red-600 hover:text-red-700 hover:bg-red-50 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        title="Delete interview"
                      >
                        {deletingInterview === row.id ? (
                          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                        ) : (
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        )}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
