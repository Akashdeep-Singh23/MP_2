import React from 'react';
import { CalendarDays, Check, Clock3 } from 'lucide-react';

export default function HistoryView({ history }) {
  const records = history?.history || [];
  return <div className="app-content">
    <div className="workout-heading"><div><p className="eyebrow"><span className="status-dot" /> YOUR TRAINING LOG</p><h1>Every session<br className="mobile-break" /> counts.</h1><p className="heading-copy">A private record of the workouts you’ve completed.</p></div></div>
    {!records.length ? <div className="app-empty history-empty"><span className="empty-mark"><CalendarDays size={20} /></span><h2>No sessions logged yet.</h2><p>When you mark a workout complete, it will be saved here.</p></div> : <section className="history-list" aria-label="Completed workouts">{records.map((item) => <article key={item.id} className="history-row"><span className="history-check"><Check size={16} /></span><div className="history-main"><h2>{item.session_name}</h2><p>{item.primary_goal}</p></div><time><Clock3 size={14} />{item.completed_at ? new Date(item.completed_at).toLocaleString() : 'Date unavailable'}</time></article>)}</section>}
  </div>;
}
