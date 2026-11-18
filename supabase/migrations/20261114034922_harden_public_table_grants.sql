-- Enable row-level security for every application table.
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercises ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_exercises ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_alternatives ENABLE ROW LEVEL SECURITY;

-- Replace Supabase's broad default table grants with the least access required.
REVOKE ALL PRIVILEGES ON TABLE profiles, workout_history, exercises, workout_sessions,
    session_exercises, exercise_alternatives FROM anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON TABLE profiles TO authenticated;
GRANT SELECT, INSERT ON TABLE workout_history TO authenticated;
GRANT SELECT ON TABLE exercises, workout_sessions, session_exercises,
    exercise_alternatives TO anon, authenticated;

-- Profiles and history are private to their authenticated owner.
DROP POLICY IF EXISTS "Users can manage own profile" ON profiles;
CREATE POLICY "Users can manage own profile" ON profiles FOR ALL TO authenticated
    USING ((SELECT auth.uid()) = user_id)
    WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can manage own history" ON workout_history;
DROP POLICY IF EXISTS "Users can insert own history" ON workout_history;
CREATE POLICY "Users can manage own history" ON workout_history FOR SELECT TO authenticated
    USING ((SELECT auth.uid()) = user_id);
CREATE POLICY "Users can insert own history" ON workout_history FOR INSERT TO authenticated
    WITH CHECK ((SELECT auth.uid()) = user_id);

-- Only reviewed, approved catalogue records are visible through the Data API.
DROP POLICY IF EXISTS "Anyone can read approved exercises" ON exercises;
CREATE POLICY "Anyone can read approved exercises" ON exercises FOR SELECT TO anon, authenticated
    USING (review_status = 'approved');

DROP POLICY IF EXISTS "Anyone can read approved sessions" ON workout_sessions;
CREATE POLICY "Anyone can read approved sessions" ON workout_sessions FOR SELECT TO anon, authenticated
    USING (review_status = 'approved');

DROP POLICY IF EXISTS "Anyone can read session exercises" ON session_exercises;
CREATE POLICY "Anyone can read session exercises" ON session_exercises FOR SELECT TO anon, authenticated
    USING (
        EXISTS (
            SELECT 1 FROM workout_sessions ws
            WHERE ws.workout_id = session_exercises.workout_id AND ws.review_status = 'approved'
        )
        AND EXISTS (
            SELECT 1 FROM exercises e
            WHERE e.exercise_id = session_exercises.exercise_id AND e.review_status = 'approved'
        )
    );

DROP POLICY IF EXISTS "Anyone can read approved alternatives" ON exercise_alternatives;
CREATE POLICY "Anyone can read approved alternatives" ON exercise_alternatives FOR SELECT TO anon, authenticated
    USING (review_status = 'approved');
