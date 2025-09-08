// C:\Users\archi\Downloads\Folder2\frontend\src\index.js

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import axios from 'axios';

// --- Global Axios Configuration ---
axios.defaults.withCredentials = true;

// NOTE: Since Firebase handles token management on the client-side,
// and your backend seems to use a separate CSRF token system,
// we will keep the CSRF token logic as is.
let csrfToken = null;

const fetchCsrfToken = async() => {
    try {
        const response = await axios.get('http://localhost:8000/api/auth/csrf-token/');
        csrfToken = response.data.csrfToken;
        axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
        console.log("CSRF token fetched and set globally:", csrfToken);
    } catch (error) {
        console.error("Failed to fetch CSRF token:", error);
    }
};

fetchCsrfToken().then(() => {
    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(
        <React.StrictMode>
          <App />
        </React.StrictMode>
      );
});