// C:\Users\archi\Downloads\Folder2\frontend\src\components\common\Card.jsx

import React from 'react';
import { Card as MuiCard, CardContent } from '@mui/material';

const Card = ({ 
  children, 
  elevation = 1,
  sx = {},
  ...props 
}) => {
  return (
    <MuiCard
      elevation={elevation}
      sx={{
        borderRadius: 2,
        overflow: 'hidden',
        ...sx
      }}
      {...props}
    >
      <CardContent>
        {children}
      </CardContent>
    </MuiCard>
  );
};

export default Card;