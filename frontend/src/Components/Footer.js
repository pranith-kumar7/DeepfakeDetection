import React from 'react';
import { Link } from 'react-router-dom';

function Footer() {
  return (
    <footer className="footer">
      <div className="footer__content">
        <div>
          <h3>MyDetector</h3>
          <p>Deepfake detection for images, videos, and frame-level model evidence.</p>
        </div>

        <div className="footer__links">
          <Link to="/">Home</Link>
          <Link to="/auth">Sign In</Link>
          <Link to="/detect">Analyze</Link>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
