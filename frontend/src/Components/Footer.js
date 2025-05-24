import React from 'react';

function Footer() {
  return (
    <footer
      style={{
        backgroundColor: '#222',
        color: '#eee',
        textAlign: 'center',
        padding: '20px 10px',
        marginTop: '40px',
        fontSize: '14px',
        fontFamily: 'Arial, sans-serif',
      }}
    >
      <p style={{ margin: '5px 0' }}>
        © 2025 MyDetector. All rights reserved.
      </p>
      <p style={{ margin: '5px 0' }}>
        Contact us at{' '}
        <a href="mailto:support@yourapp.com" style={{ color: '#55aaff', textDecoration: 'none' }}>
          support@MyDetector.com
        </a>
      </p>
      <p style={{ margin: '5px 0' }}>
        <a href="/" style={{ color: '#55aaff', margin: '0 10px', textDecoration: 'none' }}>
          Home
        </a>
        |
        <a href="/detect" style={{ color: '#55aaff', margin: '0 10px', textDecoration: 'none' }}>
          Detect Video
        </a>
        |
        <a href="/detect" style={{ color: '#55aaff', margin: '0 10px', textDecoration: 'none' }}>
          Detect Image
        </a>
        |
        <a href="/" style={{ color: '#55aaff', margin: '0 10px', textDecoration: 'none' }}>
          About
        </a>
        |
        <a href="/" style={{ color: '#55aaff', margin: '0 10px', textDecoration: 'none' }}>
          Contact
        </a>
      </p>
    </footer>
  );
}

export default Footer;
