// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
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
