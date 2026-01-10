export type InterviewStatus = "pending" | "in_progress" | "completed" | "expired";

export interface Interview {
  id: string;
  token: string;
  candidateName: string;
  candidateEmail: string;
  status: InterviewStatus;
  createdAt: string;
  completedAt?: string;
}

export interface InterviewSession {
  interviewId: string;
  currentQuestion: number;
  answers: Answer[];
  startedAt: string;
}

export interface Answer {
  questionNumber: number;
  audioUrl?: string;
  transcript?: string;
  submittedAt: string;
}
