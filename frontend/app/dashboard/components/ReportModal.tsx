"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabaseClient";
import { Evaluation } from "@/types/evaluation";

interface ReportModalProps {
  interviewId: string;
  onClose: () => void;
}

function ScoreCard({ label, score, maxScore = 100 }: { label: string; score: number; maxScore?: number }) {
  const percentage = (score / maxScore) * 100;
  const getColor = () => {
    if (percentage >= 80) return "bg-green-500";
    if (percentage >= 60) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className="text-2xl font-bold text-gray-900">{score.toFixed(1)}</div>
      <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
        <div
          className={`h-2 rounded-full ${getColor()}`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  );
}

function LevelBadge({ label, level }: { label: string; level: string | null }) {
  if (!level) return null;
  
  const getColorClass = () => {
    switch (level) {
      case "C2": return "bg-purple-100 text-purple-800";
      case "C1": return "bg-blue-100 text-blue-800";
      case "B2": return "bg-green-100 text-green-800";
      case "B1": return "bg-yellow-100 text-yellow-800";
      case "A2": return "bg-orange-100 text-orange-800";
      case "A1": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <span className={`inline-block px-3 py-1 rounded-full text-lg font-semibold ${getColorClass()}`}>
        {level}
      </span>
    </div>
  );
}

export function ReportModal({ interviewId, onClose }: ReportModalProps) {
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [candidateName, setCandidateName] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvaluation = async () => {
      try {
        const { data, error: fetchError } = await supabase
          .from("interviews")
          .select("name, evaluation")
          .eq("id", interviewId)
          .single();

        if (fetchError) {
          console.error("Failed to fetch evaluation:", fetchError);
          setError("Failed to load evaluation data");
          return;
        }

        setCandidateName(data?.name || "");
        setEvaluation(data?.evaluation as Evaluation | null);
      } catch (err) {
        console.error("Failed to fetch evaluation:", err);
        setError("Failed to load evaluation data");
      } finally {
        setLoading(false);
      }
    };

    fetchEvaluation();
  }, [interviewId]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Interview Report</h2>
            {candidateName && (
              <p className="text-gray-600 mt-1">{candidateName}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors p-2 hover:bg-gray-100 rounded-full"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading evaluation...</span>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-600">{error}</p>
          </div>
        ) : evaluation ? (
          <div className="space-y-6">
            {/* Overall Score */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl p-6 text-white">
              <div className="text-sm opacity-80 mb-1">Overall Score</div>
              <div className="text-5xl font-bold">{evaluation.overall_score.toFixed(1)}</div>
              <div className="mt-2 text-sm opacity-80">
                {evaluation.completed ? "Assessment Completed" : "Assessment In Progress"}
              </div>
            </div>

            {/* Score Breakdown */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Score Breakdown</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <ScoreCard label="Fluency" score={evaluation.fluency_score} />
                <ScoreCard label="Grammar" score={evaluation.grammar_score} />
                <LevelBadge label="Reading Level" level={evaluation.reading_level} />
                {evaluation.proficiency_level && (
                  <LevelBadge label="Proficiency" level={evaluation.proficiency_level} />
                )}
              </div>
            </div>

            {/* Exercise Summary */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Exercise Summary</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-gray-900">{evaluation.total_exercises}</div>
                  <div className="text-sm text-gray-600">Total Exercises</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-blue-600">{evaluation.speaking_exercises}</div>
                  <div className="text-sm text-gray-600">Speaking</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-green-600">{evaluation.reading_exercises}</div>
                  <div className="text-sm text-gray-600">Reading</div>
                </div>
              </div>
            </div>

            {/* Feedback */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Feedback</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700 leading-relaxed">{evaluation.feedback}</p>
              </div>
            </div>

            {/* Evaluation Timestamp */}
            {evaluation.evaluated_at && (
              <div className="text-sm text-gray-500 text-right">
                Evaluated on {new Date(evaluation.evaluated_at).toLocaleString()}
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-2">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-gray-600">No evaluation available yet</p>
            <p className="text-sm text-gray-400 mt-1">The evaluation will appear here once the interview is completed</p>
          </div>
        )}
      </div>
    </div>
  );
}
