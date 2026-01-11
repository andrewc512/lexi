"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { supabase } from "@/lib/supabaseClient";
import { CandidateForm } from "./components/CandidateForm";
import { InterviewTable } from "./components/InterviewTable";
import { ReportModal } from "./components/ReportModal";

export default function DashboardPage() {
  const router = useRouter();
  const [selectedInterview, setSelectedInterview] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [user, setUser] = useState<{ name?: string; email?: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        setUser({
          name: user.user_metadata?.full_name || user.user_metadata?.name || user.email?.split('@')[0],
          email: user.email,
        });
      }
      setLoading(false);
    };
    getUser();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };

    if (dropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownOpen]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push("/");
  };

  const handleInterviewCreated = () => {
    // Trigger a refresh of the interview table
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation Header */}
      <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
        <nav className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            </div>
            <span className="text-2xl font-semibold text-gray-900">Lexi</span>
          </Link>

          {/* User Info */}
          <div className="flex items-center space-x-4">
            {!loading && user && (
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="flex items-center space-x-2 text-gray-900 hover:text-blue-600 transition-colors font-medium"
                >
                  <span>{user.name || user.email}</span>
                  <svg
                    className={`w-4 h-4 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                {dropdownOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                    {user.email && (
                      <div className="px-4 py-2 border-b border-gray-200">
                        <div className="text-xs text-gray-500 mb-1">Email</div>
                        <div className="text-sm font-medium text-gray-900">{user.email}</div>
                      </div>
                    )}
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <CandidateForm onInterviewCreated={handleInterviewCreated} />
        </div>
        <div className="lg:col-span-2">
          <InterviewTable 
            onSelectInterview={setSelectedInterview} 
            refreshTrigger={refreshTrigger}
          />
        </div>
      </div>

        {selectedInterview && (
          <ReportModal
            interviewId={selectedInterview}
            onClose={() => setSelectedInterview(null)}
          />
        )}
      </div>
    </div>
  );
}
