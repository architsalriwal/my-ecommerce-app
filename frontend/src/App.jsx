// C:\Users\archi\Downloads\Folder2\frontend\src\App.jsx

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline, Box, CircularProgress, Typography } from '@mui/material';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';

// Layout Components
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';

import PrivateRoute from './components/PrivateRoute'; 

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Cart from './pages/Cart';
import ProductDetail from './components/product/ProductDetail'; 
import Profile from './pages/Profile';
import OrderHistory from './pages/OrderHistory';
import OrderDetails from './pages/OrderDetails';
import Checkout from './pages/Checkout'; 
import OrderSuccess from './pages/OrderSuccess'; 

// Stripe Integration
import { loadStripe } from '@stripe/stripe-js'; // Only loadStripe here, Elements will be in Checkout

// Create theme
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
      try {
        const loadedStripe = await loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY || 'pk_test_YOUR_FALLBACK_PUBLIC_KEY');
        if (loadedStripe) {
          console.log('App.jsx: Stripe.js loaded successfully!');
          setStripeLoadedInstance(loadedStripe); 
        } else {
          console.error('App.jsx: Stripe.js failed to load, loadedStripe was null.');
          setStripeLoadingError('Failed to load Stripe. Please check your public key.');
        }
      } catch (error) {
        console.error('App.jsx: Error loading Stripe.js:', error);
        setStripeLoadingError(`Error loading Stripe: ${error.message}`);
      }
    };

    loadStripeKey();
  }, []); // Run once on mount to load Stripe

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
          {/* We pass the loaded Stripe instance as a prop to components that need it */}
          {/* The Elements provider will now be handled inside Checkout.jsx */}
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