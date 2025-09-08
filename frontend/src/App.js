import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box, CircularProgress, Typography } from '@mui/material';
import Navbar from './components/layout/Navbar.jsx';
import Footer from './components/layout/Footer.jsx';
import Home from './pages/Home.jsx';
import Login from './pages/Login.jsx';
import Register from './pages/Register.jsx';
import Cart from './pages/Cart.jsx';
import ProductDetail from './components/product/ProductDetail.jsx';
import Profile from './pages/Profile.jsx';
import OrderHistory from './pages/OrderHistory.jsx';
import OrderDetails from './pages/OrderDetails.jsx';
import Wishlist from './pages/Wishlist.jsx';

import Checkout from './pages/Checkout.jsx';
import OrderSuccess from './pages/OrderSuccess.jsx';

import { loadStripe } from '@stripe/stripe-js';

import PrivateRoute from './components/common/PrivateRoute.jsx'; // Assuming this path is correct

import { AuthProvider } from './context/AuthContext.jsx';
import { CartProvider } from './context/CartContext.jsx';

// Import the new test component
import TestProfile from './components/TestProfile.jsx';

const theme = createTheme({
    palette: {
        primary: {
            main: '#1976d2',
        },
        secondary: {
            main: '#dc004e',
        },
    },
    typography: {
        fontFamily: [
            '-apple-system',
            'BlinkMacSystemFont',
            '"Segoe UI"',
            'Roboto',
            '"Helvetica Neue"',
            'Arial',
            'sans-serif',
        ].join(','),
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                },
            },
        },
    },
});

function App() {
    const [stripeLoadedInstance, setStripeLoadedInstance] = useState(null); // Store the actual Stripe object
    const [stripeLoadingError, setStripeLoadingError] = useState(null);

    useEffect(() => {
        const loadStripeKey = async () => {
            console.log('App.js: Attempting to load Stripe.js...');
            try {
                // Ensure REACT_APP_STRIPE_PUBLIC_KEY is correctly set in your .env.local
                const loadedStripe = await loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY || 'pk_test_YOUR_FALLBACK_PUBLIC_KEY');
                if (loadedStripe) {
                    console.log('App.js: Stripe.js loaded successfully! Setting instance.');
                    setStripeLoadedInstance(loadedStripe);
                } else {
                    console.error('App.js: Stripe.js failed to load, loadedStripe was null. Check public key.');
                    setStripeLoadingError('Failed to load Stripe. Please check your public key.');
                }
            } catch (error) {
                console.error('App.js: Error loading Stripe.js:', error);
                setStripeLoadingError(`Error loading Stripe: ${error.message}`);
            }
        };

        loadStripeKey();
    }, []); // Run once on mount to load Stripe

    // Log the stripeLoadedInstance whenever it changes
    useEffect(() => {
        console.log('App.js: stripeLoadedInstance state changed to:', stripeLoadedInstance);
    }, [stripeLoadedInstance]);


    if (stripeLoadingError) {
        return (
            <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh', textAlign: 'center' }}>
                <Typography variant="h5" color="error">Error Loading Application</Typography>
                <Typography variant="body1" color="error">{stripeLoadingError}</Typography>
                <Typography variant="body2" sx={{ mt: 2 }}>Please check your internet connection or Stripe configuration.</Typography>
            </Box>
        );
    }

    // Display loading spinner until Stripe.js is loaded
    if (!stripeLoadedInstance) {
        return (
            <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <CircularProgress />
                <Typography sx={{ mt: 2 }}>Loading payment services...</Typography>
            </Box>
        );
    }

    // Only render the main application content (including Router) once Stripe is loaded
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <AuthProvider>
                <CartProvider>
                    <Router>
                        <div className="app" style={{
                            display: 'flex',
                            flexDirection: 'column',
                            minHeight: '100vh'
                        }}>
                            <Navbar />
                            <main className="main-content" style={{
                                flex: 1,
                                padding: '20px 0'
                            }}>
                                <Routes>
                                    <Route path="/" element={<Home />} />
                                    <Route path="/login" element={<Login />} />
                                    <Route path="/register" element={<Register />} />
                                    <Route path="/cart" element={<Cart />} />
                                    <Route path="/products/:id" element={<ProductDetail />} />

                                    {/* Protected Routes */}
                                    <Route element={<PrivateRoute />}>
                                        <Route path="/profile" element={<Profile />} />
                                        <Route path="/orders" element={<OrderHistory />} />
                                        <Route path="/orders/:orderId" element={<OrderDetails />} />
                                        {/* Pass the loaded stripe instance to Checkout */}
                                        <Route path="/checkout" element={<Checkout stripe={stripeLoadedInstance} />} />
                                        <Route path="/order-success/:orderUid" element={<OrderSuccess />} />
                                        <Route path="/wishlist" element={<Wishlist />} />

                                        {/* NEW: Test route for Cognito authentication */}
                                        <Route path="/test-profile" element={<TestProfile />} />
                                    </Route>
                                </Routes>
                            </main>
                            <Footer />
                        </div>
                    </Router>
                </CartProvider>
            </AuthProvider>
        </ThemeProvider>
    );
}

export default App;
