// C:\Users\archi\Downloads\Folder2\frontend\src\firebase.js

import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyDXHe9WecPQwdyP3Np2CbXkOOZroOJIss8",
    authDomain: "ecommerce-app-14cdd.firebaseapp.com",
    projectId: "ecommerce-app-14cdd",
    storageBucket: "ecommerce-app-14cdd.firebasestorage.app",
    messagingSenderId: "218950534683",
    appId: "1:218950534683:web:8a6de7f0500b7980fb9abe",
    measurementId: "G-7XMSYCKS9P"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// Export Firebase services for use in other components
export const auth = getAuth(app);
export const db = getFirestore(app);
