// C:\Users\archi\Downloads\Folder2\frontend\src\services\api.js

import axios from 'axios';
import { getAuth } from "firebase/auth";

const api = axios.create({
    baseURL: 'http://localhost:8000/api/',
});

// Use an async request interceptor to attach the Firebase ID Token
api.interceptors.request.use(async(config) => {
    try {
        const auth = getAuth();
        const user = auth.currentUser;

        if (user) {
            // Get the Firebase ID Token. This is an asynchronous operation.
            const firebaseIdToken = await user.getIdToken();
            console.log("API Interceptor: Found Firebase user. Attaching ID Token to headers.");
            // Use "Bearer" prefix for the JWT
            config.headers.Authorization = `Bearer ${firebaseIdToken}`;
            console.log("Bas check karne ke liye")
        } else {
            console.log("API Interceptor: No Firebase user found. Authorization header will not be set.");
            // If no user is authenticated, clear the Authorization header
            delete config.headers.Authorization;
        }
    } catch (error) {
        console.error("Error getting Firebase ID Token:", error);
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

export default api;
