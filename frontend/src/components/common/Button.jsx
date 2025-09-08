// C:\Users\archi\Downloads\Folder2\frontend\src\components\common\Button.jsx

import React from 'react';
import { Button as MuiButton } from '@mui/material';

const Button = ({ 
  children, 
  variant = 'contained', 
  color = 'primary', 
  fullWidth = false,
  ...props 
}) => {
  return (
    <MuiButton
      variant={variant}
      color={color}
      fullWidth={fullWidth}
      {...props}
    >
      {children}
    </MuiButton>
  );
};

export default Button;