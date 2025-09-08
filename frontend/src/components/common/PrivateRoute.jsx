// C:\Users\archi\Downloads\Folder2\frontend\src\components\common\PrivateRoute.jsx

import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext'; // Adjust path based on your context location

const PrivateRoute = () => {
  const { isAuthenticated, loading } = useAuth(); // Get authentication status and loading state from AuthContext

  // While authentication status is being determined, show nothing or a loading indicator
  if (loading) {
    return null; // Or return a loading spinner/component
  }

  // If authenticated, render the child routes (Outlet)
  // Otherwise, redirect to the login page
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default PrivateRoute;
