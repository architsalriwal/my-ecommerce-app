// C:\Users\archi\Downloads\Folder2\frontend\src\components\layout\Alert.jsx

import React from 'react';
import { Alert as MuiAlert, Snackbar } from '@mui/material';

const Alert = ({ open, message, severity, onClose }) => {
  return (
    <Snackbar
      open={open}
      autoHideDuration={6000}
      onClose={onClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
    >
      <MuiAlert onClose={onClose} severity={severity} sx={{ width: '100%' }}>
        {message}
      </MuiAlert>
    </Snackbar>
  );
};

export default Alert;