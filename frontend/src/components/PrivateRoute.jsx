// C:\Users\archi\Downloads\Folder2\frontend\src\components\PrivateRoute.jsx

import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // Adjust path if AuthContext is elsewhere
import { CircularProgress, Box, Typography } from '@mui/material'; // For loading indicator

const PrivateRoute = () => {
    const { isAuthenticated, loading } = useAuth(); // Assume AuthContext provides isAuthenticated and loading

    if (loading) {
        // You might want to show a full-page loading spinner while authentication status is being determined
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Loading user...</Typography>
            </Box>
        );
    }

    // If authenticated, render the nested routes (children of this Route)
    // Otherwise, redirect to the login page
    return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default PrivateRoute;