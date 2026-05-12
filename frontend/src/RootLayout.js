import React, { useEffect, useState } from 'react';
import Navigation from './Components/Navigation';
import { Outlet } from 'react-router-dom';
import Footer from './Components/Footer';

function RootLayout() {
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('deepfake-user');
    if (savedUser) {
      try {
        setCurrentUser(JSON.parse(savedUser));
      } catch (error) {
        localStorage.removeItem('deepfake-user');
      }
    }
  }, []);

  const handleAuthChange = (user) => {
    if (user) {
      localStorage.setItem('deepfake-user', JSON.stringify(user));
      setCurrentUser(user);
      return;
    }

    localStorage.removeItem('deepfake-user');
    setCurrentUser(null);
  };

  return (
    <div className="app-shell">
      <Navigation currentUser={currentUser} onSignOut={() => handleAuthChange(null)} />
      <main className="app-main">
        <Outlet context={{ currentUser, setCurrentUser: handleAuthChange }} />
      </main>
      <Footer />
    </div>
  );
}

export default RootLayout;
