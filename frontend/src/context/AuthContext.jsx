// C:\Users\archi\Downloads\Folder2\frontend\src\context\AuthContext.jsx

import React, { createContext, useState, useContext, useEffect } from 'react';
import { onAuthStateChanged, signOut } from "firebase/auth";
import { auth } from '../firebase'; // Import the auth instance you already created

// Create the context
const AuthContext = createContext(null);

// Custom hook to use the context easily
export const useAuth = () => useContext(AuthContext);

// The provider component that will wrap the application
export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Use Firebase's onAuthStateChanged listener to get real-time auth status.
        // This is the official and most reliable way to handle Firebase authentication state.
        const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
            setUser(currentUser);
            setLoading(false);
        });

        // Cleanup the listener when the component unmounts.
        // This prevents memory leaks.
        return () => unsubscribe();
    }, []);

    const logout = async () => {
        try {
            // Use Firebase's signOut method to log the user out.
            await signOut(auth);
            // The onAuthStateChanged listener will automatically update the state,
            // so we don't need to manually set the user to null here.
        } catch (error) {
            console.error("Error signing out:", error);
        }
    };

    // The context value to be provided to children components
    const value = {
        user,
        loading,
        isAuthenticated: !!user, // A simple boolean for convenience
        logout,
    };

    // Render the children, providing them access to the context
    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};
