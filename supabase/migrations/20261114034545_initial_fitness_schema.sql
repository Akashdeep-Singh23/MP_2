-- Database Schema for Personalized AI-Driven Fitness & Workout Recommendation System
-- Engine: PostgreSQL 15+ (Hosted Supabase)
-- Authority: documentation/DATABASE.md

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. PROFILES TABLE
CREATE TABLE IF NOT EXISTS profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    primary_goal VARCHAR(50) NOT NULL CHECK (primary_goal IN (
        'Muscle gain', 'Fat loss', 'Endurance', 'General fitness', 'Strength improvement', 'Flexibility and mobility'
    )),
    fitness_level VARCHAR(20) NOT NULL CHECK (fitness_level IN ('Beginner', 'Intermediate', 'Advanced')),
    equipment TEXT[] NOT NULL,
    available_duration_minutes INT NOT NULL CHECK (available_duration_minutes BETWEEN 5 AND 180),
    safety_hold BOOLEAN NOT NULL DEFAULT FALSE,
    safety_screening_status VARCHAR(30) NOT NULL DEFAULT 'CLEARED' CHECK (
        safety_screening_status IN ('CLEARED', 'HOLD', 'URGENT_SYMPTOMS')
    ),
    safety_confirmed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_equipment_non_empty CHECK (array_length(equipment, 1) > 0)
);

-- 2. EXERCISES TABLE
CREATE TABLE IF NOT EXISTS exercises (
    exercise_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    difficulty VARCHAR(20) CHECK (difficulty IN ('Beginner', 'Intermediate', 'Advanced') OR difficulty IS NULL),
    equipment_requirements TEXT[] NOT NULL DEFAULT '{}',
    instructions TEXT NOT NULL DEFAULT '',
    primary_muscles TEXT[] NOT NULL DEFAULT '{}',
    secondary_muscles TEXT[] DEFAULT '{}',
    source_equipment VARCHAR(100),
    source_level VARCHAR(50),
    movement_pattern VARCHAR(50),
    exercise_category VARCHAR(50) NOT NULL,
    source_reference VARCHAR(255) NOT NULL,
    review_status VARCHAR(20) NOT NULL DEFAULT 'quarantined' CHECK (review_status IN ('quarantined', 'reviewed', 'approved')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Keep previously initialized databases aligned with the source-catalogue fields.
ALTER TABLE exercises ALTER COLUMN difficulty DROP NOT NULL;
ALTER TABLE exercises ALTER COLUMN instructions SET DEFAULT '';
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS source_equipment VARCHAR(100);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS source_level VARCHAR(50);

-- 3. WORKOUT_SESSIONS TABLE
CREATE TABLE IF NOT EXISTS workout_sessions (
    workout_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    primary_goal VARCHAR(50) NOT NULL CHECK (primary_goal IN (
        'Muscle gain', 'Fat loss', 'Endurance', 'General fitness', 'Strength improvement', 'Flexibility and mobility'
    )),
    secondary_goals TEXT[] DEFAULT '{}',
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('Beginner', 'Intermediate', 'Advanced')),
    duration_minutes INT NOT NULL CHECK (duration_minutes > 0),
    required_equipment TEXT[] NOT NULL DEFAULT '{}',
    workout_type VARCHAR(50) NOT NULL,
    instructions TEXT NOT NULL,
    source_attribution VARCHAR(255) NOT NULL,
    review_status VARCHAR(20) NOT NULL DEFAULT 'quarantined' CHECK (review_status IN ('quarantined', 'reviewed', 'approved')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. SESSION_EXERCISES JOIN TABLE
CREATE TABLE IF NOT EXISTS session_exercises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_id VARCHAR(100) NOT NULL REFERENCES workout_sessions(workout_id) ON DELETE CASCADE,
    exercise_id VARCHAR(100) NOT NULL REFERENCES exercises(exercise_id) ON DELETE RESTRICT,
    sequence_number INT NOT NULL CHECK (sequence_number > 0),
    sets INT CHECK (sets > 0),
    reps VARCHAR(50),
    duration_seconds INT CHECK (duration_seconds >= 0),
    rest_seconds INT NOT NULL DEFAULT 60 CHECK (rest_seconds >= 0),
    notes TEXT,
    CONSTRAINT uq_session_sequence UNIQUE (workout_id, sequence_number),
    CONSTRAINT chk_prescription_valid CHECK (
        (sets IS NOT NULL AND reps IS NOT NULL) OR (duration_seconds IS NOT NULL)
    )
);

-- 5. EXERCISE_ALTERNATIVES TABLE
CREATE TABLE IF NOT EXISTS exercise_alternatives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_exercise_id VARCHAR(100) NOT NULL REFERENCES exercises(exercise_id) ON DELETE CASCADE,
    alternative_exercise_id VARCHAR(100) NOT NULL REFERENCES exercises(exercise_id) ON DELETE CASCADE,
    applicability_context VARCHAR(100) NOT NULL,
    alternative_equipment TEXT[] NOT NULL DEFAULT '{}',
    review_status VARCHAR(20) NOT NULL DEFAULT 'quarantined' CHECK (review_status IN ('quarantined', 'approved')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_exercise_alt UNIQUE (original_exercise_id, alternative_exercise_id, applicability_context)
);

-- 6. WORKOUT_HISTORY TABLE
CREATE TABLE IF NOT EXISTS workout_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    workout_id VARCHAR(100) NOT NULL REFERENCES workout_sessions(workout_id) ON DELETE RESTRICT,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_snapshot JSONB NOT NULL,
    idempotency_key VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_idempotency UNIQUE (user_id, idempotency_key)
);

-- Indexes for optimized querying
CREATE INDEX IF NOT EXISTS idx_profiles_user ON profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_approved ON workout_sessions(primary_goal, difficulty) WHERE review_status = 'approved';
CREATE INDEX IF NOT EXISTS idx_exercises_approved ON exercises(review_status) WHERE review_status = 'approved';
CREATE INDEX IF NOT EXISTS idx_session_exercises_workout ON session_exercises(workout_id, sequence_number);
CREATE INDEX IF NOT EXISTS idx_workout_history_user_completed ON workout_history(user_id, completed_at DESC);

-- Enable Row Level Security on all application tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercises ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_exercises ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_alternatives ENABLE ROW LEVEL SECURITY;

-- The API sets the authenticated role and verified JWT claims per transaction.
GRANT SELECT, INSERT, UPDATE ON profiles TO authenticated;
GRANT SELECT, INSERT ON workout_history TO authenticated;
GRANT SELECT ON exercises, workout_sessions, session_exercises, exercise_alternatives TO authenticated;

DROP POLICY IF EXISTS "Users can manage own profile" ON profiles;
CREATE POLICY "Users can manage own profile" ON profiles FOR ALL TO authenticated
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage own history" ON workout_history;
CREATE POLICY "Users can manage own history" ON workout_history FOR ALL TO authenticated
    USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Anyone can read approved exercises" ON exercises;
CREATE POLICY "Anyone can read approved exercises" ON exercises FOR SELECT
    USING (review_status = 'approved');

DROP POLICY IF EXISTS "Anyone can read approved sessions" ON workout_sessions;
CREATE POLICY "Anyone can read approved sessions" ON workout_sessions FOR SELECT
    USING (review_status = 'approved');

DROP POLICY IF EXISTS "Anyone can read session exercises" ON session_exercises;
CREATE POLICY "Anyone can read session exercises" ON session_exercises FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM workout_sessions ws
        WHERE ws.workout_id = session_exercises.workout_id AND ws.review_status = 'approved'
    ));

DROP POLICY IF EXISTS "Anyone can read approved alternatives" ON exercise_alternatives;
CREATE POLICY "Anyone can read approved alternatives" ON exercise_alternatives FOR SELECT
    USING (review_status = 'approved');