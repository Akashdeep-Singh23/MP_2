import React from 'react';
import { Activity, Apple, ArrowRightFromLine, Clock3, Dumbbell, Settings2, TrendingUp } from 'lucide-react';

const navItems = [
  { id: 'recommendations', label: 'Workouts', Icon: Dumbbell },
  { id: 'dashboard', label: 'Progress', Icon: TrendingUp },
  { id: 'history', label: 'History', Icon: Clock3 },
  { id: 'nutrition', label: 'Nutrition', Icon: Apple },
  { id: 'settings', label: 'Settings', Icon: Settings2 },
];

export default function Header({ activeTab, onTabChange, profile, onSignOut }) {
  return <header className="app-header">
    <div className="app-header-inner">
      <button type="button" className="wordmark" onClick={() => onTabChange('recommendations')} aria-label="Go to workouts"><span className="brand-mark">F</span><span>FORM<span className="text-accent">/</span></span></button>
      <nav className="app-nav" aria-label="Main navigation">{navItems.map(({ id, label, Icon }) => <button key={id} type="button" onClick={() => onTabChange(id)} aria-current={activeTab === id ? 'page' : undefined} className={`app-nav-link ${activeTab === id ? 'is-active' : ''}`}><Icon size={16} /><span>{label}</span></button>)}</nav>
      <div className="app-account">{profile && <span className="account-goal"><Activity size={14} />{profile.primary_goal}</span>}<button type="button" onClick={onSignOut} className="signout-button"><ArrowRightFromLine size={16} /><span>Sign out</span></button></div>
    </div>
  </header>;
}
