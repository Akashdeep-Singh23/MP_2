import React, { useEffect } from 'react';

const steps = [
  ['01', 'Set the constraints', 'Pick a goal, your available equipment and the time you have.'],
  ['02', 'Choose a session', 'See approved workouts that fit the preferences on your profile.'],
  ['03', 'Get on with it', 'Follow each movement, use the rest timer and record when you finish.'],
];

export default function LandingPage({ onGetStarted, onSignIn }) {
  useEffect(() => {
    const elements = document.querySelectorAll('[data-reveal]');
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      elements.forEach((element) => element.classList.add('is-visible'));
      return undefined;
    }
    const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {
      if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); }
    }), { threshold: 0.15 });
    elements.forEach((element) => observer.observe(element));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="landing-shell">
      <header className="site-nav">
        <div className="site-nav-inner">
          <a href="#top" className="wordmark" aria-label="Form home"><span className="brand-mark">F</span><span>FORM<span className="text-accent">/</span></span></a>
          <nav className="site-links" aria-label="Main navigation"><a href="#how-it-works">How it works</a><a href="#approach">Approach</a></nav>
          <div className="site-actions"><button onClick={onSignIn} className="text-button">Sign in</button><button onClick={onGetStarted} className="button-primary">Build my plan <span aria-hidden="true">↗</span></button></div>
        </div>
      </header>

      <main id="top">
        <section className="landing-hero">
          <div className="hero-copy">
            <p className="eyebrow"><span className="status-dot" /> TRAINING, WITHOUT THE NOISE</p>
            <h1>Make room<br />for a <span>good</span><br />session.</h1>
            <p className="hero-description">A practical workout plan shaped around your time, experience and equipment. Pick what works today; the rest stays simple.</p>
            <div className="hero-actions"><button onClick={onGetStarted} className="button-primary button-large">Set up your profile <span aria-hidden="true">↗</span></button><a href="#how-it-works" className="text-button">Take a look around <span aria-hidden="true">↓</span></a></div>
            <div className="hero-note"><span>01</span><span>Set your pace</span><span className="note-rule" /><span>Keep it repeatable</span></div>
          </div>
          <div className="hero-panel" aria-label="Workout planning steps">
            <div className="hero-panel-head"><span>YOUR TRAINING, YOUR TERMS</span><span className="panel-index">F / 01</span></div>
            <div className="panel-phrase">TODAY<br /><span>COUNTS.</span></div>
            <div className="panel-lines" aria-hidden="true"><i /><i /><i /><i /><i /><i /><i /><i /></div>
            <div className="panel-footer"><span>GOAL</span><b>YOUR CHOICE</b><span>EQUIPMENT</span><b>WHAT YOU HAVE</b><span>TIME</span><b>WHAT YOU CAN GIVE</b></div>
          </div>
        </section>

        <section className="tagline-section" aria-label="Product promise" data-reveal>
          <p className="eyebrow">LESS GUESSING. MORE DOING.</p>
          <h2>A plan that fits<br />the day you have.</h2>
          <p>Keep the goal clear. Make the session manageable. Come back when you’re ready.</p>
        </section>

        <section id="how-it-works" className="steps-section">
          <div className="section-heading" data-reveal><p className="eyebrow">THE ROUTINE</p><h2>Three steps.<br />Then get moving.</h2><p>Your choices guide the recommendations. You stay in control of the session.</p></div>
          <div className="steps-grid" data-reveal>{steps.map(([number, title, body]) => <article key={number} className="step-item"><span className="step-number">{number}</span><h3>{title}</h3><p>{body}</p></article>)}</div>
        </section>

        <section id="approach" className="approach-section" data-reveal>
          <div><p className="eyebrow">BUILT AROUND YOUR REAL LIFE</p><h2>Useful detail.<br />No made-up promises.</h2></div>
          <div className="approach-copy"><p>FORM uses the preferences you save to find suitable sessions from its workout library. Open a session for the movements and instructions, then log it when you finish.</p><div className="approach-points"><span><b>01</b> Your available time stays visible</span><span><b>02</b> Equipment filters the list</span><span><b>03</b> Progress comes from sessions you log</span></div><p className="fine-print">Exercise descriptions include material from <a href="https://github.com/yuhonas/free-exercise-db" target="_blank" rel="noreferrer">Free Exercise DB</a> (Unlicense). Training guidance is educational and is not medical advice.</p></div>
        </section>
      </main>
      <footer className="site-footer"><a href="#top" className="wordmark"><span className="brand-mark">F</span><span>FORM<span className="text-accent">/</span></span></a><span>A routine you can return to.</span></footer>
      <div className="mobile-cta"><button onClick={onGetStarted} className="button-primary">Build my plan <span aria-hidden="true">↗</span></button></div>
    </div>
  );
}
