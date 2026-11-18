import React, { useState } from 'react';
import { Settings, Trash2, AlertTriangle, ShieldCheck, User } from 'lucide-react';

export default function AccountSettings({ profile, onEditProfile, onDeleteAccount }) {
  const [confirmText, setConfirmText] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState('');

  const handleDelete = async () => {
    if (confirmText !== "DELETE_MY_ACCOUNT") return;
    setDeleting(true);
    setDeleteError('');
    try {
      await onDeleteAccount(confirmText);
    } catch (err) {
      setDeleteError(err.message || 'The account could not be deleted. Please try again.');
      setDeleting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Account & Profile Settings</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Manage your fitness configuration and data privacy settings.
        </p>
      </div>

      {/* Profile Overview Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-slate-100 rounded-xl text-slate-600">
              <User className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">Recommendation Profile</h3>
              <p className="text-xs text-slate-500">Active attributes used for filtering and ML scoring</p>
            </div>
          </div>
          <button
            onClick={onEditProfile}
            className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 bg-indigo-50 px-3.5 py-1.5 rounded-lg transition"
          >
            Update Profile
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div>
            <span className="text-slate-400 block font-medium">Primary Goal</span>
            <span className="font-semibold text-slate-900">{profile?.primary_goal || "Not set"}</span>
          </div>
          <div>
            <span className="text-slate-400 block font-medium">Fitness Level</span>
            <span className="font-semibold text-slate-900">{profile?.fitness_level || "Not set"}</span>
          </div>
          <div>
            <span className="text-slate-400 block font-medium">Available Time</span>
            <span className="font-semibold text-slate-900">{profile?.available_duration_minutes} min</span>
          </div>
          <div>
            <span className="text-slate-400 block font-medium">Safety Status</span>
            <span className={`font-semibold ${profile?.safety_hold ? "text-rose-600" : "text-emerald-600"}`}>
              {profile?.safety_screening_status || "CLEARED"}
            </span>
          </div>
        </div>

        <div className="pt-2 text-xs">
          <span className="text-slate-400 block font-medium mb-1">Equipment Set</span>
          <div className="flex flex-wrap gap-1.5">
            {profile?.equipment?.map((eq) => (
              <span key={eq} className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[11px] font-medium">
                {eq}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Danger Zone: Account Deletion */}
      <div className="bg-white rounded-2xl border border-rose-200 p-6 shadow-sm space-y-4">
        <div>
          <h3 className="text-sm font-bold text-rose-900 flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-600" />
            <span>Danger Zone</span>
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Permanently delete your user identity, fitness profile, and all completed workout history.
          </p>
        </div>

        <div className="pt-2">
          <button
            onClick={() => setShowModal(true)}
            className="bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-semibold px-4 py-2 rounded-xl transition flex items-center space-x-2"
          >
            <Trash2 className="w-4 h-4" />
            <span>Delete Account & Private Records</span>
          </button>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900">Confirm Permanent Account Deletion</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              This action cannot be undone. All your private data (profile, safety screening logs, and entire workout completion history) will be permanently purged from PostgreSQL and Supabase Auth.
            </p>
            <div className="space-y-2">
              {deleteError && <p role="alert" className="inline-error">{deleteError}</p>}
              <label className="text-xs font-bold text-slate-700 block">
                Type <code className="bg-slate-100 text-rose-600 px-1 py-0.5 rounded">DELETE_MY_ACCOUNT</code> to confirm:
              </label>
              <input
                type="text"
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                placeholder="DELETE_MY_ACCOUNT"
                className="w-full text-xs p-2.5 rounded-lg border border-slate-300 font-mono focus:ring-2 focus:ring-rose-500"
              />
            </div>
            <div className="flex justify-end space-x-3 pt-2">
              <button
                onClick={() => { setShowModal(false); setConfirmText(""); }}
                className="text-xs font-semibold px-4 py-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={confirmText !== "DELETE_MY_ACCOUNT" || deleting}
                className="bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold px-4 py-2 rounded-lg transition disabled:opacity-40"
              >
                {deleting ? "Purging Data..." : "Confirm & Delete"}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
