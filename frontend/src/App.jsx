import React, { useState, useEffect } from 'react';
import LandingPage from './components/LandingPage';
import Header from './components/Header';
import ProfileSetup from './components/ProfileSetup';
import RecommendationsView from './components/RecommendationsView';
import SessionDetailModal from './components/SessionDetailModal';
import DashboardView from './components/DashboardView';
import HistoryView from './components/HistoryView';
import NutritionView from './components/NutritionView';
import AccountSettings from './components/AccountSettings';
import AuthPanel from './components/AuthPanel';
import { api } from './services/api';
import { isSupabaseConfigured, supabase } from './services/supabase';

export default function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [activeTab, setActiveTab] = useState('landing');
  const [profile, setProfile] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedWorkout, setSelectedWorkout] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [history, setHistory] = useState(null);
  const [nutritionData, setNutritionData] = useState(null);

  const [loading, setLoading] = useState(false);
  const [recLoading, setRecLoading] = useState(false);
  const [error, setError] = useState(null);
  const [authMode, setAuthMode] = useState(null);

  const handleSignOut = async () => {
    try {
      if (supabase) await supabase.auth.signOut({ scope: 'local' });
    } catch {
      // Clear local application state even if the auth client cannot be reached.
    } finally {
      setUser(null);
      setToken(null);
      setProfile(null);
      setRecommendations([]);
      setActiveTab('landing');
    }
  };

  const fetchProfileAndData = async (currentToken) => {
    if (!currentToken) return;
    setLoading(true);
    try {
      let p;
      try {
        p = await api.getProfile(currentToken);
      } catch (requestError) {
        if (requestError.status === 404) p = null;
        else throw requestError;
      }
      setProfile(p);
      if (p) {
        fetchRecommendations(currentToken);
        fetchDashboardAndHistory(currentToken);
      } else {
        setActiveTab('profile_setup');
      }
    } catch (err) {
      setError(err);
      if (err.status === 401) await handleSignOut();
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async (currentToken = token) => {
    if (!currentToken) return;
    setRecLoading(true);
    setError(null);
    try {
      const res = await api.getRecommendations(currentToken);
      setRecommendations(res.results || []);
    } catch (err) {
      setError(err);
      if (err.status === 409) {
        // Safety hold
        setProfile(prev => prev ? { ...prev, safety_hold: true, safety_screening_status: err.details?.status || "HOLD" } : prev);
      }
    } finally {
      setRecLoading(false);
    }
  };

  const fetchDashboardAndHistory = async (currentToken = token) => {
    if (!currentToken) return;
    try {
      const dash = await api.getDashboard(currentToken).catch(() => null);
      const hist = await api.getHistory(currentToken).catch(() => null);
      setDashboard(dash);
      setHistory(hist);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchNutrition = async () => {
    try {
      const data = await api.getNutrition();
      setNutritionData(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (!supabase) return undefined;
    let active = true;
    const applySession = (event, session) => {
      if (!active) return;
      setUser(session?.user || null);
      setToken(session?.access_token || null);
      setError(null);
      if (session?.access_token) {
        if (event === 'SIGNED_IN' || event === 'INITIAL_SESSION') {
          setAuthMode(null);
          setActiveTab('recommendations');
        }
        fetchProfileAndData(session.access_token);
      } else {
        setProfile(null);
        setActiveTab('landing');
      }
    };
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => applySession(event, session));
    return () => { active = false; subscription.unsubscribe(); };
  }, []);

  useEffect(() => {
    if (activeTab === 'nutrition') fetchNutrition();
  }, [activeTab]);

  const handleSaveProfile = async (profileData) => {
    const saved = await api.updateProfile(profileData, token);
    setProfile(saved);
    setActiveTab('recommendations');
    fetchRecommendations(token);
    fetchDashboardAndHistory(token);
  };

  const handleMarkComplete = async (workoutId) => {
    const idempotencyKey = `complete-${workoutId}-${Date.now()}`;
    await api.logCompletion(workoutId, idempotencyKey, token);
    await fetchDashboardAndHistory(token);
  };

  const handleDeleteAccount = async (confirmation) => {
    await api.deleteAccount(confirmation, token);
    handleSignOut();
  };

  // If user is on public landing page
  if (!user) {
    return <>
      <LandingPage
        onGetStarted={() => setAuthMode('signup')}
        onSignIn={() => setAuthMode('signin')}
      />
      {authMode && <AuthPanel initialMode={authMode} onClose={() => setAuthMode(null)} />}
      {!isSupabaseConfigured && (
        <div className="fixed bottom-4 left-1/2 z-40 -translate-x-1/2 border border-[#555] bg-[#1F1F1F] px-4 py-3 text-sm text-white shadow" role="status">
          Connect a Supabase project by setting VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.
        </div>
      )}
    </>;
  }

  return (
    <div className="min-h-screen bg-[#181818] text-white flex flex-col">
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        profile={profile}
        onSignOut={handleSignOut}
      />

      <main className="flex-1 pb-16">
        {error && (
          <div role="alert" className="mx-auto mt-4 max-w-5xl rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
            {error.message || 'The request could not be completed. Please try again.'}
          </div>
        )}
        {activeTab === 'profile_setup' && (
          <ProfileSetup
            initialProfile={profile}
            onSave={handleSaveProfile}
            onCancel={() => profile && setActiveTab('recommendations')}
          />
        )}

        {activeTab === 'recommendations' && (
          <RecommendationsView
            profile={profile}
            recommendations={recommendations}
            loading={recLoading || (loading && !profile)}
            error={error}
            onSelectWorkout={setSelectedWorkout}
            onEditProfile={() => setActiveTab('profile_setup')}
            onRefresh={() => fetchRecommendations(token)}
          />
        )}

        {activeTab === 'dashboard' && (
          <DashboardView
            dashboard={dashboard}
            onNavigateToWorkouts={() => setActiveTab('recommendations')}
          />
        )}

        {activeTab === 'history' && (
          <HistoryView history={history} />
        )}

        {activeTab === 'nutrition' && (
          <NutritionView nutritionData={nutritionData} />
        )}

        {activeTab === 'settings' && (
          <AccountSettings
            profile={profile}
            onEditProfile={() => setActiveTab('profile_setup')}
            onDeleteAccount={handleDeleteAccount}
          />
        )}
      </main>

      {/* Workout Detail Modal */}
      {selectedWorkout && (
        <SessionDetailModal
          session={selectedWorkout}
          onClose={() => setSelectedWorkout(null)}
          onMarkComplete={handleMarkComplete}
        />
      )}
    </div>
  );
}
