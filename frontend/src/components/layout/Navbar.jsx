// C:\Users\archi\Downloads\Folder2\frontend\src\components\layout\Navbar.jsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Box,
  InputBase
} from '@mui/material';
import {
  ShoppingCart,
  Person,
  Search,
  Favorite
} from '@mui/icons-material';

const Navbar = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  // Destructure 'cart' and 'loading' from useCart()
  const { cart, loading } = useCart(); 
  const [anchorEl, setAnchorEl] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    handleClose();
    navigate('/login');
  };

  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      navigate(`/search?q=${searchQuery}`);
    }
  };

  // Calculate cart item count safely
  // If cart is null or loading, show 0. Otherwise, count items in cart.cart_items array.
  const cartItemCount = (cart && cart.cart_items) ? cart.cart_items.length : 0;
  // Alternatively, if your backend returns `total_items` in the CartSerializer:
  // const cartItemCount = (cart && cart.total_cart_items) ? cart.total_cart_items : 0;
  // Using cart.cart_items.length directly from the fetched data is generally more reliable
  // if you're displaying a badge that shows the number of distinct items.
  // If you want total quantity (e.g., 2 shirts + 3 pants = 5 total items), you'd need a different calculation:
  // const totalQuantity = (cart && cart.cart_items) ? cart.cart_items.reduce((sum, item) => sum + item.quantity, 0) : 0;


  return (
    <AppBar position="sticky">
      <Toolbar>
        <Typography
          variant="h6"
          component="div"
          sx={{ cursor: 'pointer' }}
          onClick={() => navigate('/')}
        >
          Your Store
        </Typography>

        <Box sx={{ 
          position: 'relative',
          ml: 2,
          flexGrow: 1,
          maxWidth: 500
        }}>
          <InputBase
            placeholder="Search products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleSearch}
            sx={{
              backgroundColor: 'rgba(255, 255, 255, 0.15)',
              borderRadius: 1,
              px: 2,
              py: 1,
              width: '100%',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.25)',
              },
            }}
          />
          <Search sx={{ 
            position: 'absolute',
            right: 8,
            top: '50%',
            transform: 'translateY(-50%)',
            color: 'white'
          }} />
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton 
            color="inherit"
            onClick={() => navigate('/wishlist')}
          >
            <Favorite />
          </IconButton>

          <IconButton 
            color="inherit"
            onClick={() => navigate('/cart')}
          >
            {/* Safely check for cart and cart_items before accessing length */}
            <Badge badgeContent={cartItemCount} color="error">
              <ShoppingCart />
            </Badge>
          </IconButton>

          {user ? (
            <>
              <IconButton
                color="inherit"
                onClick={handleMenu}
              >
                <Person />
              </IconButton>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleClose}
              >
                <MenuItem onClick={() => {
                  navigate('/profile');
                  handleClose();
                }}>
                  Profile
                </MenuItem>
                <MenuItem onClick={() => {
                  navigate('/orders');
                  handleClose();
                }}>
                  Orders
                </MenuItem>
                <MenuItem onClick={handleLogout}>
                  Logout
                </MenuItem>
              </Menu>
            </>
          ) : (
            <Button 
              color="inherit"
              onClick={() => navigate('/login')}
            >
              Login
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;