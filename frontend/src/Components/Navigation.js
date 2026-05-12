import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaArrowRight, FaFingerprint, FaUserCircle } from 'react-icons/fa';

function Navigation({ currentUser, onSignOut }) {
  const navigate = useNavigate();

  const handleSignOut = () => {
    onSignOut();
    navigate('/');
  };

  return (
    <header className="topbar">
      <div className="topbar__inner">
        <Link className="brand" to="/">
          <span className="brand__badge">
            <FaFingerprint />
          </span>
          <span>
            <strong>MyDetector</strong>
            <small>Deepfake analysis</small>
          </span>
        </Link>

        <nav className="topbar__nav">
          <Link to="/">Home</Link>
          <Link to="/detect">Analyze</Link>
          {currentUser ? (
            <div className="account-chip">
              <FaUserCircle />
              <span>{currentUser.name}</span>
              <button type="button" className="ghost-button" onClick={handleSignOut}>
                Sign out
              </button>
            </div>
          ) : (
            <Link className="primary-link" to="/auth">
              Sign in
              <FaArrowRight />
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}

export default Navigation;
