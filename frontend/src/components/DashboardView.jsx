import React from 'react';
import { ArrowUpRight, CalendarDays, Check, Clock3, TrendingUp } from 'lucide-react';

export default function DashboardView({ dashboard, onNavigateToWorkouts }) {
  if (!dashboard) return <div className="app-content session-loading" role="status">Loading your training history…</div>;
  const { total_completed = 0, recent_activity = [], weekly_trends = [], goal_wise_counts = {} } = dashboard;
  const latestWeek = weekly_trends.at(-1)?.completion_count ?? 0;
  const maxCount = Math.max(...weekly_trends.map((week) => week.completion_count || 0), 1);

  return <div className="app-content">
    <div className="workout-heading"><div><p className="eyebrow"><span className="status-dot" /> YOUR TRAINING LOG</p><h1>Progress, as<br className="mobile-break" /> you build it.</h1><p className="heading-copy">A record of the sessions you’ve completed.</p></div><button onClick={onNavigateToWorkouts} className="quiet-button"><ArrowUpRight size={15} /> View workouts</button></div>
    <div className="progress-stats"><article><span>COMPLETED SESSIONS</span><strong>{total_completed}</strong><small><Check size={14} /> Saved to your log</small></article><article><span>THIS WEEK</span><strong>{latestWeek}</strong><small><CalendarDays size={14} /> Completed sessions</small></article><article><span>RECENT ACTIVITY</span><strong>{recent_activity.length}</strong><small><Clock3 size={14} /> Entries shown below</small></article></div>
    {total_completed === 0 ? <div className="app-empty progress-empty"><span className="empty-mark"><TrendingUp size={20} /></span><h2>Your log starts with one session.</h2><p>Complete a workout and it will appear here with your weekly activity.</p><button onClick={onNavigateToWorkouts} className="button-primary">Choose a workout <ArrowUpRight size={16} /></button></div> : <div className="progress-grid">
      <section className="data-panel"><div className="panel-title"><div><p className="eyebrow">WEEK BY WEEK</p><h2>Session count</h2></div><span>Completed</span></div>{weekly_trends.length ? <div className="week-chart">{weekly_trends.map((week, index) => { const count = week.completion_count || 0; return <div className="week-column" key={`${week.week_start}-${index}`}><strong>{count}</strong><div className="week-bar-track"><i style={{ height: `${Math.max((count / maxCount) * 100, count ? 8 : 2)}%` }} /></div><span>{week.week_start?.slice(5) || ''}</span></div>; })}</div> : <p className="panel-empty">Weekly activity will appear here after you complete workouts.</p>}</section>
      <section className="data-panel"><div className="panel-title"><div><p className="eyebrow">BY GOAL</p><h2>Sessions completed</h2></div></div>{Object.entries(goal_wise_counts).length ? <div className="goal-counts">{Object.entries(goal_wise_counts).map(([goal, count]) => <div className="goal-count" key={goal}><div><span>{goal}</span><b>{count}</b></div><div className="goal-track"><i style={{ width: `${Math.min((count / Math.max(total_completed, 1)) * 100, 100)}%` }} /></div></div>)}</div> : <p className="panel-empty">No goal breakdown is available yet.</p>}</section>
    </div>}
    {recent_activity.length > 0 && <section className="recent-panel"><div className="panel-title"><div><p className="eyebrow">LATEST ENTRIES</p><h2>Recent sessions</h2></div></div>{recent_activity.slice(0, 5).map((item, index) => <div className="recent-row" key={`${item.session_name}-${item.completed_at}-${index}`}><span className="recent-check"><Check size={15} /></span><div><b>{item.session_name}</b><small>{item.primary_goal}</small></div><time>{item.completed_at ? new Date(item.completed_at).toLocaleDateString() : ''}</time></div>)}</section>}
  </div>;
}
