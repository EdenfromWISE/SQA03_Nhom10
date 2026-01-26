// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { getSavedTheme, applyTheme } from './theme';
import { env } from './config/env';

const root = ReactDOM.createRoot(document.getElementById('root'));
// Initialize theme on startup
applyTheme(getSavedTheme());
root.render(
  // <React.StrictMode>
    <GoogleOAuthProvider clientId={env.GOOGLE_CLIENT_ID}>
      <App />
    </GoogleOAuthProvider>
  // { </React.StrictMode> }
);