import React, { useState, useEffect } from 'react';
import { X, Clock3, Dumbbell, Play, Pause, RotateCcw, CheckCircle2 } from 'lucide-react';

export default function SessionDetailModal({ session, onClose, onMarkComplete }) {
  const [timerRunning, setTimerRunning] = useState(false);
  const [activeTimerSeconds, setActiveTimerSeconds] = useState(60);
  const [completing, setCompleting] = useState(false);
  const [completionError, setCompletionError] = useState('');

  useEffect(() => {
    if (!timerRunning || activeTimerSeconds <= 0) { if (activeTimerSeconds === 0) setTimerRunning(false); return undefined; }
    const interval = setInterval(() => setActiveTimerSeconds((prev) => prev - 1), 1000);
    return () => clearInterval(interval);
  }, [timerRunning, activeTimerSeconds]);

  const startRestTimer = (seconds) => { setActiveTimerSeconds(seconds); setTimerRunning(true); };
  const handleComplete = async () => {
    setCompleting(true); setCompletionError('');
    try { await onMarkComplete(session.workout_id); onClose(); }
    catch (err) { setCompletionError(err.message || 'Your session could not be saved. Please try again.'); }
    finally { setCompleting(false); }
  };

  if (!session) return null;
  const formatTime = (seconds) => `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;

  return <div className="session-modal-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <section className="session-modal" role="dialog" aria-modal="true" aria-labelledby="session-title">
      <header className="session-modal-header"><div><p className="eyebrow"><span className="status-dot" /> {session.primary_goal || session.workout_type} <span>·</span> {session.difficulty}</p><h2 id="session-title">{session.name}</h2><p className="session-modal-meta"><span><Clock3 size={14} /> {session.duration_minutes} minutes</span><span><Dumbbell size={14} /> {session.required_equipment?.join(', ') || 'Bodyweight only'}</span></p>{session.source_attribution && <p className="session-source">{session.source_attribution}</p>}</div><button type="button" onClick={onClose} className="session-close" aria-label="Close workout details"><X size={20} /></button></header>
      <div className="session-modal-body">
        {completionError && <p role="alert" className="inline-error">{completionError}</p>}
        {session.instructions && <div className="session-instructions"><span>SESSION NOTES</span><p>{session.instructions}</p></div>}
        <div className="rest-timer"><div><span>REST TIMER</span><strong>{formatTime(activeTimerSeconds)}</strong></div><div className="timer-actions"><button type="button" onClick={() => setTimerRunning(!timerRunning)} aria-label={timerRunning ? 'Pause timer' : 'Start timer'}>{timerRunning ? <Pause size={17} /> : <Play size={17} />}</button><button type="button" onClick={() => { setTimerRunning(false); setActiveTimerSeconds(60); }} aria-label="Reset timer"><RotateCcw size={16} /></button></div></div>
        <div className="exercise-heading"><h3>Movements</h3><span>{session.exercises?.length || 0} exercises</span></div>
        <div className="exercise-list">{session.exercises?.map((exercise) => <article className="exercise-row" key={exercise.sequence_number}><span className="exercise-number">{String(exercise.sequence_number).padStart(2, '0')}</span><div className="exercise-copy"><h4>{exercise.name}</h4><p>{exercise.instructions}</p>{exercise.notes && <small>{exercise.notes}</small>}</div><div className="exercise-actions"><span>{exercise.sets ? `${exercise.sets} sets × ${exercise.reps || 'reps'}` : `${exercise.duration_seconds}s`}</span><button type="button" onClick={() => startRestTimer(exercise.rest_seconds || 60)}>{exercise.rest_seconds || 60}s rest</button></div></article>)}</div>
      </div>
      <footer className="session-modal-footer"><button type="button" className="quiet-button" onClick={onClose}>Close</button><button type="button" onClick={handleComplete} disabled={completing} className="button-primary"><CheckCircle2 size={16} />{completing ? 'Saving…' : 'Mark complete'}</button></footer>
    </section>
  </div>;
}
