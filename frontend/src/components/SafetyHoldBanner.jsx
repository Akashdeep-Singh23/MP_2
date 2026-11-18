import React from 'react';
import { ShieldAlert, AlertCircle, RefreshCw } from 'lucide-react';

export default function SafetyHoldBanner({ status, onReviewScreening }) {
  const isUrgent = status === "URGENT_SYMPTOMS";

  return (
    <div className={`rounded-2xl p-6 border mb-8 ${
      isUrgent
        ? "bg-rose-50 border-rose-300 text-rose-900"
        : "bg-amber-50 border-amber-300 text-amber-900"
    }`}>
      <div className="flex items-start space-x-4">
        <div className={`p-3 rounded-xl ${isUrgent ? "bg-rose-200 text-rose-800" : "bg-amber-200 text-amber-800"}`}>
          <ShieldAlert className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <h3 className="text-base font-bold">
              {isUrgent ? "Emergency Health Precaution Active" : "Personalized Recommendations Temporarily Paused"}
            </h3>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-bold uppercase bg-white/60">
              {status}
            </span>
          </div>

          <p className="text-xs mt-2 leading-relaxed">
            {isUrgent
              ? "You indicated experiencing urgent cardiovascular symptoms (chest pain, shortness of breath, or dizziness). You must not perform high-intensity exercise and should seek immediate medical evaluation."
              : "You indicated an active injury, unexplained pain, or physical limitation during your physical safety screening. In compliance with safety protocols, personalized workout recommendations are paused until your symptoms resolve."}
          </p>

          <div className="mt-4 flex flex-wrap items-center gap-3">
            <button
              onClick={onReviewScreening}
              className="bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 text-xs font-semibold px-4 py-2 rounded-lg transition shadow-sm inline-flex items-center space-x-2"
            >
              <RefreshCw className="w-3.5 h-3.5 text-slate-600" />
              <span>Review / Update Safety Screening</span>
            </button>
            <span className="text-xs text-slate-500 italic">
              Confirmation of resolution is required before recommendations can resume.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
