import React from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import heroImage from '../Assets/image.jpg';

function Webhome() {
  const { currentUser } = useOutletContext();

  return (
    <section className="hero-page">
      <div className="hero-card" style={{ backgroundImage: `linear-gradient(90deg, rgba(9, 18, 36, 0.92), rgba(9, 18, 36, 0.7), rgba(9, 18, 36, 0.22)), url(${heroImage})` }}>
        <div className="hero-copy">
          <span className="eyebrow">Deepfake intelligence platform</span>
          <h1>MyDetector</h1>
          <p>
            Analyze images and videos with model-backed prediction scores, frame-level evidence,
            confidence metrics, and a clear result dashboard.
          </p>

          <div className="hero-actions">
            <Link className="hero-button hero-button--primary" to="/detect">
              Start analysis
            </Link>
            <Link className="hero-button hero-button--secondary" to={currentUser ? '/detect' : '/auth'}>
              {currentUser ? 'Continue as ' + currentUser.name : 'Sign in'}
            </Link>
          </div>
        </div>

        <div className="hero-panel">
          <div className="metric-card">
            <span>Input coverage</span>
            <strong>Images + videos</strong>
          </div>
          <div className="metric-card">
            <span>Output</span>
            <strong>Scores, charts, evidence</strong>
          </div>
          <div className="metric-card">
            <span>Session</span>
            <strong>{currentUser ? 'Authenticated' : 'Sign in required'}</strong>
          </div>
        </div>
      </div>

      <div className="feature-grid">
        <article className="feature-card">
          <h3>Model-backed scoring</h3>
          <p>Separate image and video models return fake and real likelihoods with confidence.</p>
        </article>
        <article className="feature-card">
          <h3>Frame evidence</h3>
          <p>Video results include sampled frame confidence and consistency indicators.</p>
        </article>
        <article className="feature-card">
          <h3>Decision dashboard</h3>
          <p>Charts summarize likelihood, uncertainty, score gap, and risk level.</p>
        </article>
      </div>
    </section>
  );
}

export default Webhome;
