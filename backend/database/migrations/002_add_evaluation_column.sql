-- Migration: Add evaluation column to interviews table
-- Description: Stores evaluation data as JSONB for completed interviews
-- Note: This was added via Supabase Table Editor UI

-- If running manually, execute:
-- ALTER TABLE interviews ADD COLUMN IF NOT EXISTS evaluation JSONB;

-- The evaluation JSONB structure:
-- {
--   "overall_score": 85,           -- Percentage score (0-100)
--   "grammar_score": 7.5,          -- Grammar proficiency (0-10)
--   "fluency_score": 8.0,          -- Fluency proficiency (0-10)
--   "proficiency_level": "B2",     -- CEFR level (A1, A2, B1, B2, C1, C2)
--   "reading_level": "Intermediate", -- Reading proficiency level
--   "feedback": "...",             -- Summary feedback text
--   "total_exercises": 5,          -- Number of exercises completed
--   "evaluated_at": "2024-01-15T12:00:00Z"  -- Timestamp
-- }

-- Create index for querying by proficiency level (optional)
CREATE INDEX IF NOT EXISTS idx_interviews_proficiency 
    ON interviews ((evaluation->>'proficiency_level'));
