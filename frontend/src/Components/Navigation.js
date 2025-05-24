// frontend/src/components/Navigation.js
import React from 'react';
import { Link } from 'react-router-dom';
import { FaUserCircle } from 'react-icons/fa'; // User account icon

function Navigation() {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand fw-bolder" to="/">
          MyDetector
        </Link>

        <ul className="navbar-nav ms-auto align-items-center">
          <li className="nav-item">
            <Link className="nav-link fs-5 text-white fw-bold" to="/">
              Home
            </Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link fs-5 text-white fw-bold" to="/detect">
              Deepfake Detection
            </Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link fs-5 text-white fw-bold d-flex align-items-center" to="/login">
              <FaUserCircle className="me-2" size={22} />
              My Account
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navigation;
