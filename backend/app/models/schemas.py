from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

SUPPORTED_GOALS = [
    "Muscle gain",
    "Fat loss",
    "Endurance",
    "General fitness",
    "Strength improvement",
    "Flexibility and mobility"
]

FITNESS_LEVELS = ["Beginner", "Intermediate", "Advanced"]

CONTROLLED_EQUIPMENT = [
    "Bodyweight only",
    "Dumbbells",
    "Resistance bands",
    "Barbell",
    "Bench",
    "Gym machines",
    "Kettlebells",
    "Cable machine",
    "Exercise ball",
    "Foam roller"
]

class ScreeningAnswers(BaseModel):
    model_config = ConfigDict(extra="forbid")

    has_active_injury: bool = False
    has_ongoing_limitation: bool = False
    has_current_pain: bool = False
    has_urgent_symptoms: bool = False

class ProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary_goal: str = Field(min_length=1, max_length=40)
    fitness_level: str = Field(min_length=1, max_length=20)
    equipment: List[str] = Field(min_length=1, max_length=len(CONTROLLED_EQUIPMENT))
    available_duration_minutes: int = Field(ge=5, le=180)
    screening_answers: ScreeningAnswers
    confirm_cleared: bool = False

    @field_validator("primary_goal")
    def validate_goal(cls, v):
        if v not in SUPPORTED_GOALS:
            raise ValueError(f"Primary goal must be one of {SUPPORTED_GOALS}")
        return v

    @field_validator("fitness_level")
    def validate_level(cls, v):
        if v not in FITNESS_LEVELS:
            raise ValueError(f"Fitness level must be one of {FITNESS_LEVELS}")
        return v

    @field_validator("equipment")
    def validate_equipment(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Equipment selection cannot be empty. Please select your available equipment.")
        for item in v:
            if item not in CONTROLLED_EQUIPMENT:
                raise ValueError("Unrecognized equipment selection.")
        if len(set(v)) != len(v):
            raise ValueError("Equipment selections must be unique.")
        return v

class ProfileResponse(BaseModel):
    user_id: str
    primary_goal: str
    fitness_level: str
    equipment: List[str]
    available_duration_minutes: int
    safety_hold: bool
    safety_screening_status: str
    safety_confirmed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SessionExerciseItem(BaseModel):
    sequence_number: int
    exercise_id: str
    name: str
    sets: Optional[int] = None
    reps: Optional[str] = None
    duration_seconds: Optional[int] = None
    rest_seconds: int = 60
    instructions: str = ""

class WorkoutSessionItem(BaseModel):
    workout_id: str
    name: str
    primary_goal: str
    secondary_goals: List[str] = []
    difficulty: str
    duration_minutes: int
    required_equipment: List[str]
    workout_type: str
    instructions: str
    similarity_score: Optional[float] = None
    duration_caution: Optional[str] = None
    match_explanations: List[str] = []
    exercises: List[SessionExerciseItem] = []

class RecommendationsResponse(BaseModel):
    results: List[WorkoutSessionItem]
    message: str

class WorkoutHistoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workout_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
    completed_at: Optional[datetime] = None
    idempotency_key: Optional[str] = Field(default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

class WorkoutHistoryItem(BaseModel):
    id: str
    workout_id: str
    completed_at: datetime
    session_name: str
    primary_goal: str

class WorkoutHistoryListResponse(BaseModel):
    history: List[WorkoutHistoryItem]
    total_count: int

class WeeklyTrendItem(BaseModel):
    week_start: str
    completion_count: int

class DashboardResponse(BaseModel):
    total_completed: int
    recent_activity: List[WorkoutHistoryItem]
    weekly_trends: List[WeeklyTrendItem]
    goal_wise_counts: Dict[str, int]

class AccountDeleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confirmation: str = Field(min_length=1, max_length=32)

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: str

class StandardErrorResponse(BaseModel):
    error: ErrorDetail
