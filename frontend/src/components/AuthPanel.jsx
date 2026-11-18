import React, { useState } from 'react';
import { isSupabaseConfigured, supabase } from '../services/supabase';

export default function AuthPanel({ initialMode = 'signup', onClose }) {
  const [mode, setMode] = useState(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const submit = async (event) => {
    event.preventDefault(); setBusy(true); setMessage(''); setError('');
    try {
      if (!isSupabaseConfigured) throw new Error('Supabase is not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in frontend/.env.');
      const result = mode === 'signup'
        ? await supabase.auth.signUp({ email, password })
        : await supabase.auth.signInWithPassword({ email, password });
      if (result.error) throw result.error;
      if (mode === 'signup' && !result.data.session) setMessage('Account created. Check your email to confirm your address, then sign in.');
    } catch (submitError) { setError(submitError.message || 'Authentication failed. Please try again.'); }
    finally { setBusy(false); }
  };

  return (
    <div className="auth-backdrop" role="dialog" aria-modal="true" aria-labelledby="auth-title">
      <section className="auth-panel">
        <button type="button" onClick={onClose} aria-label="Close" className="auth-close">×</button>
        <p className="eyebrow text-lime">FORM<span className="text-lime">/</span> ACCOUNT</p>
        <h2 id="auth-title" className="mt-5 text-4xl font-semibold tracking-[-.05em]">{mode === 'signup' ? 'Start training.' : 'Good to have you back.'}</h2>
        <p className="mt-3 text-sm leading-6 text-[#9B9B9B]">{mode === 'signup' ? 'Create an account to save your preferences and sessions.' : 'Sign in with your email to pick up where you left off.'}</p>
        <form onSubmit={submit} className="mt-8 space-y-5">
          <label className="auth-label">Email<input required type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} className="auth-input" /></label>
          <label className="auth-label">Password<input required minLength={8} type="password" autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} value={password} onChange={(event) => setPassword(event.target.value)} className="auth-input" /></label>
          {error && <p role="alert" className="inline-error">{error}</p>}
          {message && <p role="status" className="inline-success">{message}</p>}
          <button disabled={busy} className="button-primary w-full justify-center disabled:opacity-60">{busy ? 'Please wait…' : mode === 'signup' ? 'Create account' : 'Sign in'} <span aria-hidden="true">→</span></button>
        </form>
        <p className="mt-7 text-center text-sm text-[#9B9B9B]">{mode === 'signup' ? 'Already have an account?' : 'New to Form?'}{' '}
          <button type="button" onClick={() => { setMode(mode === 'signup' ? 'signin' : 'signup'); setError(''); setMessage(''); }} className="font-semibold text-lime hover:underline">{mode === 'signup' ? 'Sign in' : 'Create an account'}</button>
        </p>
      </section>
    </div>
  );
}
