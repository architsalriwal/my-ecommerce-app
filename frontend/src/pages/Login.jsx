import React, { useState, useEffect } from 'react';
import { Container, Paper, Button, Typography, TextField, Box } from '@mui/material';
import GoogleIcon from '@mui/icons-material/Google';
import AuthService from '../services/auth.js';
import { onAuthStateChanged } from 'firebase/auth';

// Main application component
export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [message, setMessage] = useState({ text: '', isError: false });
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  // Helper function to display messages
  const showMessage = (text, isError = false) => {
    setMessage({ text, isError });
    setTimeout(() => setMessage({ text: '', isError: false }), 5000);
  };

  // Check authentication status on component load
  useEffect(() => {
    // Listen for auth state changes from Firebase
    const unsubscribe = onAuthStateChanged(AuthService.auth, async (currentUser) => {
      console.log("Login.jsx: onAuthStateChanged listener triggered. Current user:", currentUser);
      if (currentUser) {
        setIsAuthenticated(true);
        setUser(currentUser);
      } else {
        // Check if a Django token exists in localStorage after Firebase signs out
        const hasToken = AuthService.isAuthenticated();
        setIsAuthenticated(hasToken);
        if (hasToken) {
          console.log("Login.jsx: No Firebase user, but found Django token. Setting user from localStorage.");
          setUser(AuthService.getCurrentUser());
        } else {
          console.log("Login.jsx: No Firebase user or Django token. User is not authenticated.");
          setUser(null);
        }
      }
    });

    // Clean up the listener on component unmount
    return () => unsubscribe();
  }, []);

  // Handle both Sign In and Sign Up using AuthService
  const handleEmailAuth = async () => {
    try {
      if (isLoginMode) {
        console.log("Login.jsx: Attempting to sign in with email/password...");
        await AuthService.loginWithEmailAndPassword(email, password);
        showMessage("Sign in successful!", false);
      } else {
        console.log("Login.jsx: Attempting to sign up with email/password...");
        await AuthService.signUpWithEmailAndPassword(email, password);
        showMessage("Account created and signed in successfully! Welcome.", false);
      }
      setIsAuthenticated(true);
      setUser(AuthService.getCurrentUser());
    } catch (error) {
      console.error("Login.jsx: Authentication Error:", error);
      let errorMessage = "An error occurred. Please try again.";
      if (error.code === 'auth/email-already-in-use') {
        errorMessage = 'This email is already in use. Please sign in instead.';
      } else if (error.code === 'auth/invalid-credential' || error.code === 'auth/wrong-password' || error.code === 'auth/user-not-found') {
        errorMessage = 'Invalid email or password.';
      } else if (error.code === 'auth/weak-password') {
        errorMessage = 'Password should be at least 6 characters.';
      }
      showMessage(errorMessage, true);
    }
  };

  // Handle Google Sign-in using AuthService
  const handleGoogleSignIn = async () => {
    try {
      console.log("Login.jsx: Attempting to sign in with Google...");
      await AuthService.loginWithGoogle();
      showMessage("Signed in with Google successfully!", false);
      setIsAuthenticated(true);
      setUser(AuthService.getCurrentUser());
    } catch (error) {
      console.error("Login.jsx: Google Sign-in Error:", error);
      showMessage("Google sign-in failed. Please try again.", true);
    }
  };

  // Handle sign out
  const handleSignOut = async () => {
    try {
      console.log("Login.jsx: Attempting to sign out...");
      await AuthService.logout();
      showMessage("You have been signed out.", false);
      setIsAuthenticated(false);
      setUser(null);
    } catch (error) {
      console.error("Login.jsx: Sign Out Error:", error);
      showMessage("Failed to sign out.", true);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom>
          {isAuthenticated ? 'Welcome Back!' : 'Welcome to Your App'}
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          {isAuthenticated ? 'You are logged in.' : 'Please log in to continue.'}
        </Typography>

        {isAuthenticated ? (
          <Box>
            <Typography variant="body2" sx={{ my: 2 }}>
              Your User ID: **{user?.uid}**
            </Typography>
            <Button
              variant="contained"
              color="error"
              size="large"
              onClick={handleSignOut}
            >
              Sign Out
            </Button>
          </Box>
        ) : (
          <Box>
            <TextField
              fullWidth
              label="Email"
              type="email"
              variant="outlined"
              margin="normal"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              variant="outlined"
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2, mb: 2 }}>
              <Button
                variant="contained"
                color="primary"
                size="large"
                sx={{ flexGrow: 1, mr: 1 }}
                onClick={handleEmailAuth}
              >
                {isLoginMode ? 'Sign In' : 'Create Account'}
              </Button>
              <Button
                variant="outlined"
                color="primary"
                size="large"
                sx={{ flexGrow: 1, ml: 1 }}
                onClick={() => setIsLoginMode(!isLoginMode)}
              >
                {isLoginMode ? 'Switch to Sign Up' : 'Switch to Sign In'}
              </Button>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ my: 2 }}>
              OR
            </Typography>
            <Button
              variant="contained"
              startIcon={<GoogleIcon />}
              size="large"
              fullWidth
              onClick={handleGoogleSignIn}
            >
              Sign in with Google
            </Button>
          </Box>
        )}

        <Typography
          variant="body2"
          sx={{
            mt: 2,
            color: message.isError ? 'red' : 'green',
            opacity: message.text ? 1 : 0,
            transition: 'opacity 0.3s',
          }}
        >
          {message.text}
        </Typography>
      </Paper>
    </Container>
  );
}
