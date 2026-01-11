import { API_BASE_URL } from "./constants";
import { Interview } from "@/types/interview";
import { Evaluation } from "@/types/evaluation";

export const api = {
  async createInterview(data: { email: string; name: string }): Promise<Interview> {
    const response = await fetch(`${API_BASE_URL}/interviews`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async getInterviews(): Promise<Interview[]> {
    const response = await fetch(`${API_BASE_URL}/interviews`);
    return response.json();
  },

  async getInterview(id: string): Promise<Interview> {
    const response = await fetch(`${API_BASE_URL}/interviews/${id}`);
    return response.json();
  },

  async getEvaluation(interviewId: string): Promise<Evaluation> {
    const response = await fetch(`${API_BASE_URL}/interviews/${interviewId}/evaluation`);
    return response.json();
  },

  async getQuestion(questionNumber: number): Promise<{ question: string }> {
    const response = await fetch(`${API_BASE_URL}/ai/question?number=${questionNumber}`);
    return response.json();
  },

  async submitAnswer(interviewId: string, audioBlob: Blob): Promise<void> {
    const formData = new FormData();
    formData.append("audio", audioBlob);
    await fetch(`${API_BASE_URL}/interviews/${interviewId}/answer`, {
      method: "POST",
      body: formData,
    });
  },

  async sendInterviewEmail(interviewId: string, candidateEmail: string, candidateName: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/email/send-invite`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        interview_id: interviewId,
        candidate_email: candidateEmail,
        candidate_name: candidateName,
      }),
    });
    if (!response.ok) {
      throw new Error("Failed to send email");
    }
  },

  async deleteInterview(interviewId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/interviews/${interviewId}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      throw new Error("Failed to delete interview");
    }
  },
};
