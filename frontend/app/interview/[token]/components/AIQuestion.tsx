"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface AIQuestionProps {
  questionNumber: number;
}

export function AIQuestion({ questionNumber }: AIQuestionProps) {
  const [question, setQuestion] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchQuestion = async () => {
      setLoading(true);
      try {
        const data = await api.getQuestion(questionNumber);
        setQuestion(data.question);
      } catch (error) {
        console.error("Failed to fetch question:", error);
        setQuestion("Error loading question");
      } finally {
        setLoading(false);
      }
    };

    fetchQuestion();
  }, [questionNumber]);

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center gap-2 mb-4">
        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
          Question {questionNumber + 1}
        </span>
      </div>
      {loading ? (
        <p className="text-gray-500">Loading question...</p>
      ) : (
        <p className="text-lg">{question}</p>
      )}
    </div>
  );
}
