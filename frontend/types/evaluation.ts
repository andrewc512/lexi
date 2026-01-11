export interface Evaluation {
  feedback: string;
  completed: boolean;
  evaluated_at: string;
  fluency_score: number;
  grammar_score: number;
  overall_score: number;
  reading_level: string | null;
  total_exercises: number;
  proficiency_level: string | null;
  reading_exercises: number;
  speaking_exercises: number;
}
