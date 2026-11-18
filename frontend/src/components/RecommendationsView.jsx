import React from 'react';
import { AlertTriangle, ArrowUpRight, Clock3, Dumbbell, SlidersHorizontal } from 'lucide-react';
import SafetyHoldBanner from './SafetyHoldBanner';

export default function RecommendationsView({ profile, recommendations, loading, error, onSelectWorkout, onEditProfile, onRefresh }) {
  if (profile?.safety_hold) return <div className="app-content"><SafetyHoldBanner status={profile.safety_screening_status} onReviewScreening={onEditProfile} /></div>;

  if (!profile) return <div className="app-content app-empty" role={loading ? 'status' : 'alert'}>
    <p>{loading ? 'Loading your saved preferences…' : error ? 'Your saved preferences could not be loaded.' : 'No workout preferences are saved yet.'}</p>
    {!loading && <button onClick={onEditProfile} className="button-primary">Set up your profile <ArrowUpRight size={16} /></button>}
  </div>;

  const equipment = profile.equipment?.join(', ') || 'Not set';
  return (
    <div className="app-content">
      <div className="workout-heading">
        <div><p className="eyebrow"><span className="status-dot" /> YOUR TRAINING</p><h1>Pick your<br className="mobile-break" /> next session.</h1><p className="heading-copy">A focused list matched to the preferences you saved.</p></div>
        <button onClick={onEditProfile} className="quiet-button"><SlidersHorizontal size={15} /> Edit preferences</button>
      </div>
      <div className="profile-strip">
        <div><span>GOAL</span><b>{profile.primary_goal || 'Not set'}</b></div>
        <div><span>LEVEL</span><b>{profile.fitness_level || 'Not set'}</b></div>
        <div><span>AVAILABLE TIME</span><b>{profile.available_duration_minutes ?? '—'} min</b></div>
        <div className="profile-equipment"><span>EQUIPMENT</span><b>{equipment}</b></div>
      </div>

      {error && !loading && <div className="app-alert" role="alert"><AlertTriangle size={18} /><div><b>Workouts could not be loaded</b><p>{error.message || String(error)}</p><button onClick={onRefresh}>Try again</button></div></div>}
      {loading && <div className="session-loading" role="status">Finding sessions that fit your plan…</div>}
      {!loading && !error && recommendations?.length === 0 && <div className="app-empty"><span className="empty-mark"><Dumbbell size={20} /></span><h2>No matching sessions yet.</h2><p>Try another equipment option or adjust your available time.</p><button onClick={onEditProfile} className="button-primary">Adjust preferences <ArrowUpRight size={16} /></button></div>}

      {!loading && !error && recommendations?.length > 0 && <section className="session-list" aria-label="Recommended workouts">
        <div className="list-heading"><h2>Available sessions</h2><span>{recommendations.length} {recommendations.length === 1 ? 'session' : 'sessions'}</span><button onClick={onRefresh}>Refresh list</button></div>
        {recommendations.map((session, index) => <article key={session.workout_id} className="session-row">
          <div className="session-number">{String(index + 1).padStart(2, '0')}</div>
          <div className="session-main"><p className="session-kicker">{session.primary_goal || session.workout_type} <span>·</span> {session.difficulty}</p><h3>{session.name}</h3>{session.instructions && <p className="session-description">{session.instructions}</p>}<div className="session-meta"><span><Clock3 size={14} /> {session.duration_minutes} min</span><span><Dumbbell size={14} /> {session.required_equipment?.join(', ') || 'Bodyweight only'}</span></div></div>
          <button onClick={() => onSelectWorkout(session)} className="session-open" aria-label={`Open ${session.name}`}><span>View session</span><ArrowUpRight size={18} /></button>
        </article>)}
      </section>}
    </div>
  );
}
