import React from 'react';
import { useNavigate } from 'react-router-dom';

function Login() {
  const navigate = useNavigate();
  const handleSubmit = (e) => {
    e.preventDefault(); // prevent page reload
    navigate('/home'); // navigate programmatically
  };

  return (
    <div className="container mt-5">
      <h1 className="text-center text-dark mb-4">Sign In</h1>

      <form className="mx-auto p-4 border rounded shadow w-50 bg-light" onSubmit={handleSubmit}>
        <div className="mb-3">
          <input
            type="text"
            name="username"
            className="form-control"
            placeholder="Username"
          />
        </div>

        <div className="mb-4">
          <input
            type="password"
            name="userpass"
            className="form-control"
            placeholder="Password"
          />
        </div>

        <button className="btn btn-primary w-100 mb-3" type="submit">
          SignIn
        </button>

        <p className="text-center">
          Don’t have an account? <a href="/">Register</a>
        </p>
      </form>
    </div>
  );
}

export default Login;
