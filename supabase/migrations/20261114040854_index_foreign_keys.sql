CREATE INDEX IF NOT EXISTS idx_session_exercises_exercise ON public.session_exercises(exercise_id);
CREATE INDEX IF NOT EXISTS idx_exercise_alternatives_alternative ON public.exercise_alternatives(alternative_exercise_id);
CREATE INDEX IF NOT EXISTS idx_workout_history_workout ON public.workout_history(workout_id);
