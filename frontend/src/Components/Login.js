import React, { useState } from 'react';
import axios from 'axios';
import { Link, useNavigate, useOutletContext } from 'react-router-dom';

const API_BASE_URL = 'http://localhost:5000';

function Login({ initialMode = 'signin' }) {
  const navigate = useNavigate();
  const { setCurrentUser } = useOutletContext();
  const [mode, setMode] = useState(initialMode);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const isSignup = mode === 'signup';

  const handleChange = (event) => {
    setFormData((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const resetFeedback = () => {
    setError('');
    setSuccessMessage('');
  };

  const handleModeChange = (nextMode) => {
    setMode(nextMode);
    resetFeedback();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    resetFeedback();
    setLoading(true);

    try {
      const endpoint = isSignup ? '/auth/signup' : '/auth/signin';
      const payload = isSignup
        ? formData
        : { email: formData.email, password: formData.password };

      const response = await axios.post(`${API_BASE_URL}${endpoint}`, payload);
      const user = response.data.user;

      setCurrentUser(user);
      setSuccessMessage(response.data.message || 'Success');
      navigate('/detect');
    } catch (requestError) {
      setError(
        requestError.response?.data?.error ||
          'Something went wrong. Please try again in a moment.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="auth-page">
      <div className="auth-shell">
        <div className="auth-intro">
          <span className="eyebrow">Your account</span>
          <h1>{isSignup ? 'Create account' : 'Welcome back'}</h1>
          <p>
            {isSignup
              ? 'Create an account to access the analysis workspace.'
              : 'Sign in to continue to the analysis workspace.'}
          </p>
          <div className="auth-switch">
            <button
              type="button"
              className={mode === 'signin' ? 'tab-button active' : 'tab-button'}
              onClick={() => handleModeChange('signin')}
            >
              Sign in
            </button>
            <button
              type="button"
              className={mode === 'signup' ? 'tab-button active' : 'tab-button'}
              onClick={() => handleModeChange('signup')}
            >
              Sign up
            </button>
          </div>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          {isSignup && (
            <label className="field">
              <span>Full name</span>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Aman Sharma"
                required
              />
            </label>
          )}

          <label className="field">
            <span>Email</span>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="name@example.com"
              required
            />
          </label>

          <label className="field">
            <span>Password</span>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                required
              />
          </label>

          {error ? <div className="form-message form-message--error">{error}</div> : null}
          {successMessage ? (
            <div className="form-message form-message--success">{successMessage}</div>
          ) : null}

          <button className="submit-button" type="submit" disabled={loading}>
            {loading ? 'Please wait...' : isSignup ? 'Create account' : 'Sign in'}
          </button>

          <p className="auth-meta">
            {isSignup ? 'Already have an account?' : 'Need a new account?'}{' '}
            <Link to={isSignup ? '/login' : '/signup'} onClick={() => handleModeChange(isSignup ? 'signin' : 'signup')}>
              {isSignup ? 'Sign in here' : 'Create one here'}
            </Link>
          </p>
        </form>
      </div>
    </section>
  );
}

export default Login;
