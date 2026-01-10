"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Interview } from "@/types/interview";

interface InterviewTableProps {
  onSelectInterview: (id: string) => void;
}

export function InterviewTable({ onSelectInterview }: InterviewTableProps) {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInterviews = async () => {
      try {
        const data = await api.getInterviews();
        setInterviews(data);
      } catch (error) {
        console.error("Failed to fetch interviews:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchInterviews();
  }, []);

  if (loading) {
    return <div className="bg-white p-6 rounded-lg shadow">Loading...</div>;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Interviews</h2>
      <table className="w-full">
        <thead>
          <tr className="border-b">
            <th className="text-left py-2">Candidate</th>
            <th className="text-left py-2">Status</th>
            <th className="text-left py-2">Date</th>
            <th className="text-left py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {interviews.map((interview) => (
            <tr key={interview.id} className="border-b">
              <td className="py-2">{interview.candidateName}</td>
              <td className="py-2">
                <span className="px-2 py-1 text-xs rounded bg-gray-100">
                  {interview.status}
                </span>
              </td>
              <td className="py-2">{interview.createdAt}</td>
              <td className="py-2">
                <button
                  onClick={() => onSelectInterview(interview.id)}
                  className="text-blue-600 hover:underline"
                >
                  View Report
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
