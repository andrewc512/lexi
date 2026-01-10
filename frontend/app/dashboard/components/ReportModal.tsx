"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Evaluation } from "@/types/evaluation";

interface ReportModalProps {
  interviewId: string;
  onClose: () => void;
}

export function ReportModal({ interviewId, onClose }: ReportModalProps) {
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvaluation = async () => {
      try {
        const data = await api.getEvaluation(interviewId);
        setEvaluation(data);
      } catch (error) {
        console.error("Failed to fetch evaluation:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchEvaluation();
  }, [interviewId]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Interview Report</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        {loading ? (
          <p>Loading evaluation...</p>
        ) : evaluation ? (
          <div className="space-y-4">
            <div>
              <h3 className="font-medium">Overall Score</h3>
              <p className="text-2xl font-bold">{evaluation.overallScore}/100</p>
            </div>
            <div>
              <h3 className="font-medium">Summary</h3>
              <p className="text-gray-600">{evaluation.summary}</p>
            </div>
            {/* TODO: Add detailed breakdown */}
          </div>
        ) : (
          <p>No evaluation available</p>
        )}
      </div>
    </div>
  );
}
