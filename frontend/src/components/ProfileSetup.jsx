import React, { useState } from 'react';
import { ShieldCheck, Dumbbell, AlertTriangle, ArrowRight, ArrowLeft, CheckCircle2 } from 'lucide-react';

const GOALS = [
  "Muscle gain",
  "Fat loss",
  "Endurance",
  "General fitness",
  "Strength improvement",
  "Flexibility and mobility"
];

const LEVELS = [
  { id: "Beginner", desc: "0-6 months experience. Learning foundational mechanics." },
  { id: "Intermediate", desc: "6-24 months regular training. Familiar with compounds." },
  { id: "Advanced", desc: "2+ years disciplined training. High work capacity." }
];

const EQUIPMENT_LIST = [
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
];

export default function ProfileSetup({ initialProfile, onSave, onCancel }) {
  const [step, setStep] = useState(1);
  const [goal, setGoal] = useState(initialProfile?.primary_goal || "General fitness");
  const [level, setLevel] = useState(initialProfile?.fitness_level || "Beginner");
  const [equipment, setEquipment] = useState(initialProfile?.equipment || ["Bodyweight only"]);
  const [duration, setDuration] = useState(initialProfile?.available_duration_minutes || 45);

  const [injury, setInjury] = useState(false);
  const [limitation, setLimitation] = useState(false);
  const [pain, setPain] = useState(false);
  const [urgent, setUrgent] = useState(false);
  const [confirmCleared, setConfirmCleared] = useState(true);

  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const toggleEquipment = (item) => {
    if (item === "Bodyweight only") {
      setEquipment(["Bodyweight only"]);
      return;
    }
    const filtered = equipment.filter(e => e !== "Bodyweight only");
    if (filtered.includes(item)) {
      const remaining = filtered.filter(e => e !== item);
      setEquipment(remaining.length === 0 ? ["Bodyweight only"] : remaining);
    } else {
      setEquipment([...filtered, item]);
    }
  };

  const handleNext = () => {
    if (equipment.length === 0) {
      setError("Please select at least one equipment option (or Bodyweight only).");
      return;
    }
    setError(null);
    setStep(2);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    const payload = {
      primary_goal: goal,
      fitness_level: level,
      equipment,
      available_duration_minutes: duration,
      screening_answers: {
        has_active_injury: injury,
        has_ongoing_limitation: limitation,
        has_current_pain: pain,
        has_urgent_symptoms: urgent
      },
      confirm_cleared: confirmCleared
    };

    try {
      await onSave(payload);
    } catch (err) {
      setError(err.message || "Failed to save profile.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6">
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8">
        
        {/* Progress Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-5 mb-6">
          <div>
            <h2 className="text-xl font-bold text-slate-900">
              {step === 1 ? "Step 1: Fitness Preferences" : "Step 2: Physical Safety Screening"}
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              {step === 1 ? "Configure your goal, experience level, equipment, and duration." : "Mandatory safety check before recommendations."}
            </p>
          </div>
          <span className="text-xs font-semibold px-3 py-1 bg-[#e8ece3] text-[#234d3b] rounded-full">
            {step} of 2
          </span>
        </div>

        {error && (
          <div className="mb-6 bg-rose-50 border border-rose-200 rounded-xl p-4 text-xs text-rose-800 flex items-start space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-600 mt-0.5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {step === 1 && (
          <div className="space-y-6">
            {/* Primary Goal */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Primary Fitness Goal
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {GOALS.map((g) => (
                  <button
                    type="button"
                    key={g}
                    onClick={() => setGoal(g)}
                    className={`text-left p-3.5 rounded-xl border text-sm font-medium transition ${
                      goal === g
                        ? "border-[#234d3b] bg-[#e8ece3] text-[#234d3b] ring-2 ring-[#234d3b]/20"
                        : "border-slate-200 hover:border-slate-300 text-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span>{g}</span>
                      {goal === g && <CheckCircle2 className="w-4 h-4 text-[#234d3b]" />}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Fitness Level */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Fitness Experience Level
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {LEVELS.map((lvl) => (
                  <button
                    type="button"
                    key={lvl.id}
                    onClick={() => setLevel(lvl.id)}
                    className={`text-left p-4 rounded-xl border text-sm transition ${
                      level === lvl.id
                        ? "border-[#234d3b] bg-[#e8ece3] text-[#234d3b] ring-2 ring-[#234d3b]/20"
                        : "border-slate-200 hover:border-slate-300 text-slate-700"
                    }`}
                  >
                    <div className="font-semibold">{lvl.id}</div>
                    <div className="text-xs text-slate-500 mt-1">{lvl.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Available Equipment */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Available Equipment (Select all that apply)
              </label>
              <div className="flex flex-wrap gap-2">
                {EQUIPMENT_LIST.map((eq) => {
                  const isSelected = equipment.includes(eq);
                  return (
                    <button
                      type="button"
                      key={eq}
                      onClick={() => toggleEquipment(eq)}
                      className={`px-3.5 py-2 rounded-lg text-xs font-medium border transition ${
                        isSelected
                          ? "bg-[#234d3b] text-white border-[#234d3b] shadow-sm"
                          : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100"
                      }`}
                    >
                      {eq}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Duration Slider */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Available Workout Duration
                </label>
                <span className="text-sm font-bold text-[#234d3b]">{duration} minutes</span>
              </div>
              <div className="relative pb-7 pt-1">
              <input
                type="range"
                min="5"
                max="180"
                step="5"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value))}
                aria-label="Available workout duration in minutes"
                className="w-full accent-[#234d3b] h-2 bg-slate-200 rounded-lg cursor-pointer"
              />
              <div className="pointer-events-none absolute inset-x-0 top-6 h-5 text-xs text-slate-400">
                {[5, 45, 90, 180].map((minutes) => (
                  <button
                    key={minutes}
                    type="button"
                    onClick={() => setDuration(minutes)}
                    className="pointer-events-auto absolute -translate-x-1/2 whitespace-nowrap hover:text-[#234d3b]"
                    style={{ left: `${((minutes - 5) / 175) * 100}%` }}
                    aria-label={`Set duration to ${minutes} minutes`}
                  >
                    {minutes} min
                  </button>
                ))}
              </div>
              </div>
            </div>

            {/* Next Button */}
            <div className="pt-4 flex justify-end">
              <button
                type="button"
                onClick={handleNext}
                className="bg-[#234d3b] hover:bg-[#234d3b] text-white font-semibold px-6 py-2.5 rounded-xl transition flex items-center space-x-2"
              >
                <span>Proceed to Safety Check</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-800 flex items-start space-x-3">
              <ShieldCheck className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
              <div>
                <strong>Physical Safety Protocol:</strong> We enforce backend safety holds. Answering "Yes" to any active pain, injury, or limitation automatically pauses personalized recommendations until symptoms resolve.
              </div>
            </div>

            <div className="space-y-4">
              <label className="flex items-start space-x-3 p-3.5 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={injury}
                  onChange={(e) => setInjury(e.target.checked)}
                  className="mt-1 rounded text-[#234d3b] focus:ring-[#e8ece3]0 w-4 h-4"
                />
                <div className="text-xs text-slate-700">
                  <span className="font-semibold block text-slate-900">Active Joint, Bone, or Muscular Injury</span>
                  I currently have an active physical injury diagnosed by a medical professional or limiting physical exercise.
                </div>
              </label>

              <label className="flex items-start space-x-3 p-3.5 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={limitation}
                  onChange={(e) => setLimitation(e.target.checked)}
                  className="mt-1 rounded text-[#234d3b] focus:ring-[#e8ece3]0 w-4 h-4"
                />
                <div className="text-xs text-slate-700">
                  <span className="font-semibold block text-slate-900">Ongoing Physical Limitation</span>
                  I have a chronic physical restriction that prohibits high-impact movements, load-bearing, or specific postures.
                </div>
              </label>

              <label className="flex items-start space-x-3 p-3.5 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={pain}
                  onChange={(e) => setPain(e.target.checked)}
                  className="mt-1 rounded text-[#234d3b] focus:ring-[#e8ece3]0 w-4 h-4"
                />
                <div className="text-xs text-slate-700">
                  <span className="font-semibold block text-slate-900">Current or Unexplained Pain</span>
                  I am currently feeling sharp, throbbing, or unexplained pain during normal physical activities.
                </div>
              </label>

              <label className="flex items-start space-x-3 p-3.5 rounded-xl border border-rose-200 bg-rose-50/50 hover:bg-rose-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={urgent}
                  onChange={(e) => setUrgent(e.target.checked)}
                  className="mt-1 rounded text-rose-600 focus:ring-rose-500 w-4 h-4"
                />
                <div className="text-xs text-slate-700">
                  <span className="font-semibold block text-rose-900">Cardiovascular or Urgent Symptoms</span>
                  I experience chest pain, severe shortness of breath, dizziness, or fainting during or after exertion. (Requires immediate medical evaluation).
                </div>
              </label>
            </div>

            <div className="pt-2 border-t border-slate-100">
              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={confirmCleared}
                  onChange={(e) => setConfirmCleared(e.target.checked)}
                  className="mt-1 rounded text-[#234d3b] focus:ring-[#e8ece3]0 w-4 h-4"
                />
                <span className="text-xs text-slate-600">
                  I understand that this system provides educational fitness recommendations, not medical clearance. If I selected no injuries above, I confirm I am physically ready for physical activity.
                </span>
              </label>
            </div>

            <div className="pt-4 flex items-center justify-between">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="text-sm font-medium text-slate-600 hover:text-slate-900 flex items-center space-x-1"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </button>

              <button
                type="submit"
                disabled={submitting}
                className="bg-[#234d3b] hover:bg-[#234d3b] text-white font-semibold px-6 py-2.5 rounded-xl transition shadow-sm disabled:opacity-50"
              >
                {submitting ? "Saving Profile..." : "Save Profile & Finish"}
              </button>
            </div>
          </form>
        )}

      </div>
    </div>
  );
}
