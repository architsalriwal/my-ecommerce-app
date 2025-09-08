import api from './api';
import { 
    signInWithPopup, 
    GoogleAuthProvider, 
    signInWithEmailAndPassword, 
    createUserWithEmailAndPassword,
    getAuth 
} from "firebase/auth";

class AuthService {
    constructor() {
        this.auth = getAuth();
        this.googleProvider = new GoogleAuthProvider();
    }

    // Handles authentication for both Google and email/password.
    // It's a key part of your two-step authentication flow.
    async _handleLogin(userCredential) {
        try {
            const user = userCredential.user;
            console.log("AuthService: Sign-in successful. User object:", user);

            const idToken = await user.getIdToken();
            console.log("AuthService: Firebase ID token retrieved.");

            // --- NEW: Get the anonymous cart UID from localStorage ---
            const cartUid = localStorage.getItem('cart_uid');
            if (cartUid) {
                console.log(`AuthService: Found cart UID in localStorage: ${cartUid}`);
            } else {
                console.log("AuthService: No anonymous cart UID found in localStorage.");
            }
            // --- END NEW ---

            console.log("AuthService: Calling Django backend to exchange token...");
            const response = await api.post('home/auth/firebase-login/', {
                id_token: idToken,
                // --- NEW: Pass the cart UID to the backend ---
                cart_uid: cartUid,
                // --- END NEW ---
            });

            if (response.data.token) {
                console.log("AuthService: Django token received. Saving to localStorage.");
                localStorage.setItem('django_token', response.data.token);
                localStorage.setItem('user', JSON.stringify(user));
                // You may want to clear the cart_uid from localStorage after it's been linked
                // localStorage.removeItem('cart_uid');
            }
            return response.data;

        } catch (error) {
            console.error("AuthService: Token exchange or login failed:", error);
            throw error;
        }
    }

    // Method for Google Sign-In
    async loginWithGoogle() {
        try {
            console.log("AuthService: Starting Google sign-in process.");
            const userCredential = await signInWithPopup(this.auth, this.googleProvider);
            console.log("AuthService: Google sign-in successful. Calling _handleLogin...");
            return this._handleLogin(userCredential);
        } catch (error) {
            console.error("AuthService: Google sign-in failed:", error);
            throw error;
        }
    }

    // Method for Email/Password Sign-In
    async loginWithEmailAndPassword(email, password) {
        try {
            console.log("AuthService: Starting email/password sign-in process.");
            const userCredential = await signInWithEmailAndPassword(this.auth, email, password);
            console.log("AuthService: Email/password sign-in successful. Calling _handleLogin...");
            return this._handleLogin(userCredential);
        } catch (error) {
            console.error("AuthService: Email/password sign-in failed:", error);
            throw error;
        }
    }

    // New method for Email/Password Sign-Up
    async signUpWithEmailAndPassword(email, password) {
        try {
            console.log("AuthService: Starting email/password sign-up process.");
            const userCredential = await createUserWithEmailAndPassword(this.auth, email, password);
            console.log("AuthService: Email/password sign-up successful. Calling _handleLogin...");
            return this._handleLogin(userCredential);
        } catch (error) {
            console.error("AuthService: Email/password sign-up failed:", error);
            throw error;
        }
    }

    // Logout user
    async logout() {
        try {
            console.log("AuthService: Logging out...");
            localStorage.removeItem('django_token');
            localStorage.removeItem('user');
            localStorage.removeItem('cart_uid'); // Make sure to clear the cart_uid on logout
            await this.auth.signOut();
            console.log("AuthService: Logout successful.");
        } catch (error) {
            console.error('Logout error:', error);
            localStorage.removeItem('django_token');
            localStorage.removeItem('user');
            localStorage.removeItem('cart_uid');
        }
    }

    // Check if user is authenticated
    isAuthenticated() {
        const hasToken = !!localStorage.getItem('django_token');
        console.log(`AuthService: Checking if authenticated. Token exists? ${hasToken}`);
        return hasToken;
    }

    // Get current user (this can be simplified or expanded)
    getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }
}

export default new AuthService();