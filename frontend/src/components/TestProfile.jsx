// C:\Users\archi\Downloads\Folder2\frontend\src\components\TestProfile.jsx

import React, { useEffect, useState } from 'react';
import api from '../services/api.js';
import { useAuth } from '../context/AuthContext.jsx';
import { Box, Typography, Paper } from '@mui/material';

const TestProfile = () => {
    const { isAuthenticated } = useAuth();
    const [profileData, setProfileData] = useState(null);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchProfileData = async () => {
            // Don't try to fetch if the user isn't authenticated
            if (!isAuthenticated) {
                return;
            }
            try {
                // The API call will automatically include the JWT from localStorage.
                // The backend will receive this token and use our new custom backend
                // to validate it.
                const response = await api.get('/accounts/profile/');
                setProfileData(response.data);
            } catch (err) {
                console.error("Failed to fetch profile data:", err);
                setError("Failed to fetch profile data. Your token might be invalid or expired.");
            }
        };

        fetchProfileData();
    }, [isAuthenticated]);

    return (
        <Box sx={{ mt: 4 }}>
            <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h5" gutterBottom>
                    Test API Endpoint
                </Typography>
                {isAuthenticated ? (
                    profileData ? (
                        <Typography variant="body1" sx={{ mt: 2 }}>
                            **Success!**
                            <br />
                            Message from backend: "{profileData.message}"
                            <br />
                            Your username: **{profileData.username}**
                        </Typography>
                    ) : (
                        <Typography variant="body1" sx={{ mt: 2 }}>
                            Loading profile data...
                        </Typography>
                    )
                ) : (
                    <Typography variant="body1" sx={{ mt: 2 }}>
                        Please log in to see your profile data.
                    </Typography>
                )}
                {error && <Typography color="error" sx={{ mt: 2 }}>{error}</Typography>}
            </Paper>
        </Box>
    );
};

export default TestProfile;
