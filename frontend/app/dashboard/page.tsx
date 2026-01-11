"use client";

import { useState } from "react";
import { CandidateForm } from "./components/CandidateForm";
import { InterviewTable } from "./components/InterviewTable";
import { ReportModal } from "./components/ReportModal";

export default function DashboardPage() {
  const [selectedInterview, setSelectedInterview] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleInterviewCreated = () => {
    // Trigger a refresh of the interview table
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen p-8">
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
  );
}
