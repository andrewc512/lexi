-- Migration: Create session_states table for language assessments
-- Description: Stores complete state of language proficiency assessments

CREATE TABLE IF NOT EXISTS session_states (
    -- Primary key
    assessment_id TEXT PRIMARY KEY,

    -- Assessment configuration
    target_language TEXT NOT NULL,  -- Language being assessed (e.g., "Spanish")

    -- Current state
    current_phase TEXT NOT NULL DEFAULT 'intro',
        CHECK (current_phase IN ('intro', 'speaking_test', 'translation_test', 'complete')),
    current_difficulty INTEGER NOT NULL DEFAULT 1
        CHECK (current_difficulty >= 1 AND current_difficulty <= 10),

    -- Exercise tracking
    exercises_completed JSONB DEFAULT '[]'::jsonb,  -- Array of LanguageExercise objects
    speaking_exercises_done INTEGER DEFAULT 0,
    translation_exercises_done INTEGER DEFAULT 0,

    -- Scoring
    overall_grammar_score FLOAT,
    overall_fluency_score FLOAT,
    overall_proficiency_level TEXT,  -- A1, A2, B1, B2, C1, C2
        CHECK (overall_proficiency_level IS NULL OR
               overall_proficiency_level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),

    -- Metadata
    insights TEXT[] DEFAULT ARRAY[]::TEXT[],  -- Agent's observations
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes for common queries
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on phase for filtering active assessments
CREATE INDEX IF NOT EXISTS idx_session_states_phase
    ON session_states(current_phase);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_session_states_created
    ON session_states(created_at DESC);

-- Create index on target_language for analytics
CREATE INDEX IF NOT EXISTS idx_session_states_language
    ON session_states(target_language);


-- Migration: Create assessments table (parent table)
-- Description: High-level assessment metadata

CREATE TABLE IF NOT EXISTS assessments (
    id TEXT PRIMARY KEY,
    user_id TEXT,  -- Optional: Link to users table
    target_language TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'in_progress', 'completed', 'expired')),

    -- Final results
    proficiency_level TEXT,  -- Final CEFR level
        CHECK (proficiency_level IS NULL OR
               proficiency_level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
    overall_grammar_score FLOAT,
    overall_fluency_score FLOAT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Foreign key to session_states
    CONSTRAINT fk_session_state
        FOREIGN KEY (id)
        REFERENCES session_states(assessment_id)
        ON DELETE CASCADE
);

-- Create index on user_id for user lookups
CREATE INDEX IF NOT EXISTS idx_assessments_user
    ON assessments(user_id);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_assessments_status
    ON assessments(status);


-- Migration: Create exercises table (optional - for detailed storage)
-- Description: Individual exercise records for analysis

CREATE TABLE IF NOT EXISTS exercises (
    id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    exercise_type TEXT NOT NULL
        CHECK (exercise_type IN ('speaking', 'translation')),
    difficulty_level INTEGER NOT NULL
        CHECK (difficulty_level >= 1 AND difficulty_level <= 10),

    -- Exercise content
    prompt TEXT,  -- For speaking exercises
    passage TEXT,  -- For translation exercises
    passage_language TEXT,

    -- User's response
    audio_url TEXT,
    transcript TEXT,
    translation TEXT,

    -- Evaluation
    grammar_score FLOAT,
    fluency_score FLOAT,
    accuracy_score FLOAT,  -- For translation
    feedback TEXT,
    errors JSONB DEFAULT '[]'::jsonb,  -- Array of error strings

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Foreign key
    CONSTRAINT fk_assessment
        FOREIGN KEY (assessment_id)
        REFERENCES session_states(assessment_id)
        ON DELETE CASCADE
);

-- Create index on assessment_id for joins
CREATE INDEX IF NOT EXISTS idx_exercises_assessment
    ON exercises(assessment_id);

-- Create index on exercise_type for analytics
CREATE INDEX IF NOT EXISTS idx_exercises_type
    ON exercises(exercise_type);


-- Migration: Enable Row Level Security (RLS)
-- Description: Secure data access per user

ALTER TABLE session_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercises ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own assessments
-- TODO: Uncomment when auth is implemented

-- CREATE POLICY "Users can view own session states"
--     ON session_states FOR SELECT
--     USING (assessment_id IN (
--         SELECT id FROM assessments WHERE user_id = auth.uid()
--     ));

-- CREATE POLICY "Users can update own session states"
--     ON session_states FOR UPDATE
--     USING (assessment_id IN (
--         SELECT id FROM assessments WHERE user_id = auth.uid()
--     ));

-- CREATE POLICY "Users can view own assessments"
--     ON assessments FOR SELECT
--     USING (user_id = auth.uid());

-- CREATE POLICY "Users can view own exercises"
--     ON exercises FOR SELECT
--     USING (assessment_id IN (
--         SELECT id FROM assessments WHERE user_id = auth.uid()
--     ));


-- Migration: Create helpful views

-- View: Current active assessments
CREATE OR REPLACE VIEW active_assessments AS
SELECT
    a.id,
    a.target_language,
    a.status,
    s.current_phase,
    s.current_difficulty,
    s.speaking_exercises_done,
    s.translation_exercises_done,
    a.created_at,
    a.started_at
FROM assessments a
JOIN session_states s ON a.id = s.assessment_id
WHERE a.status IN ('pending', 'in_progress');


-- View: Completed assessments with results
CREATE OR REPLACE VIEW completed_assessments AS
SELECT
    a.id,
    a.user_id,
    a.target_language,
    a.proficiency_level,
    a.overall_grammar_score,
    a.overall_fluency_score,
    s.speaking_exercises_done,
    s.translation_exercises_done,
    a.created_at,
    a.completed_at,
    EXTRACT(EPOCH FROM (a.completed_at - a.started_at)) / 60 AS duration_minutes
FROM assessments a
JOIN session_states s ON a.id = s.assessment_id
WHERE a.status = 'completed';


-- Migration complete
--
-- To run this migration:
-- 1. Copy this SQL to Supabase SQL Editor
-- 2. Execute to create tables, indexes, and views
-- 3. Uncomment RLS policies when authentication is implemented
