export interface Evaluation {
  id: string;
  interviewId: string;
  overallScore: number;
  summary: string;
  criteria: EvaluationCriteria[];
  createdAt: string;
}

export interface EvaluationCriteria {
  name: string;
  score: number;
  maxScore: number;
  feedback: string;
}
