import React from 'react';
import { Apple, ShieldCheck, Info } from 'lucide-react';

export default function NutritionView({ nutritionData }) {
  const topics = nutritionData?.topics || [];
  const disclaimer = nutritionData?.disclaimer || "General educational information only. Not medical or clinical advice.";

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">General Nutrition Guidance</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Non-medical educational principles supporting energy, strength, and physical recovery.
        </p>
      </div>

      {/* Non-Medical Disclaimer Banner */}
      <div className="bg-indigo-50 border border-indigo-200 rounded-2xl p-4 text-xs text-indigo-900 flex items-start space-x-3">
        <Info className="w-5 h-5 text-indigo-600 mt-0.5 flex-shrink-0" />
        <div className="leading-relaxed">
          <strong>Educational Notice:</strong> {disclaimer} This application does not calculate personalized calories, deficits, or prescriptive diets. Consult a registered dietitian for individual clinical needs.
        </div>
      </div>

      {/* Content Topics */}
      <div className="space-y-4">
        {topics.map((t) => (
          <div key={t.id} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-2">
            <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span>{t.title}</span>
            </h3>
            <p className="text-xs font-medium text-slate-500">{t.summary}</p>
            <div className="text-xs text-slate-700 leading-relaxed pt-2 border-t border-slate-100">
              {t.content}
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}
