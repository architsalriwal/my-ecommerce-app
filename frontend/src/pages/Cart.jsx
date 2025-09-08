// C:\Users\archi\Downloads\Folder2\frontend\src\pages\Cart.jsx

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  IconButton,
  Divider,
  TextField,
  InputAdornment,
  Snackbar,
} from '@mui/material';
import { Delete as DeleteIcon, AddCircleOutline, RemoveCircleOutline } from '@mui/icons-material';
import axios from 'axios';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext'; // Assuming you need auth for cart merging

const Cart = () => {
  const { cart, fetchCart, loading, error, applyCoupon, removeCoupon } = useCart();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [couponCode, setCouponCode] = useState('');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    // Fetch cart on component mount or when auth status changes
    fetchCart();
  }, [fetchCart, isAuthenticated]);

  const handleQuantityChange = async (cartItemUid, newQuantity) => {
    if (newQuantity < 1) {
      // If quantity drops to 0, consider it a delete action
      handleRemoveItem(cartItemUid);
      return;
    }
    try {
      // Send PUT request to update quantity
      await axios.put(`/api/cart/items/${cartItemUid}/`, { quantity: newQuantity });
      fetchCart(); // Re-fetch cart to update UI
      setNotification({ open: true, message: 'Cart item quantity updated!', severity: 'success' });
    } catch (error) {
      console.error('Error updating cart item quantity:', error.response?.data || error.message);
      let errorMessage = 'Failed to update item quantity.';
      if (error.response?.data?.non_field_errors) {
        errorMessage = error.response.data.non_field_errors[0];
      } else if (error.response?.data?.quantity) {
        errorMessage = `Quantity error: ${error.response.data.quantity[0]}`;
      } else if (error.response?.data?.product_uid) { // Specific check for product_uid error
        errorMessage = `Product error: ${error.response.data.product_uid[0]}. Please remove this item.`;
      }
      setNotification({ open: true, message: errorMessage, severity: 'error' });
    }
  };

  const handleRemoveItem = async (cartItemUid) => {
    try {
      await axios.delete(`/api/cart/items/${cartItemUid}/`);
      fetchCart(); // Re-fetch cart to update UI
      setNotification({ open: true, message: 'Item removed from cart!', severity: 'success' });
    } catch (error) {
      console.error('Error removing cart item:', error.response?.data || error.message);
      let errorMessage = 'Failed to remove item from cart.';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.product_uid) {
        errorMessage = `Product error: ${error.response.data.product_uid[0]}. Item may no longer exist.`;
      }
      setNotification({ open: true, message: errorMessage, severity: 'error' });
    }
  };

  const handleApplyCoupon = async () => {
    try {
      await applyCoupon(couponCode);
      setNotification({ open: true, message: 'Coupon applied successfully!', severity: 'success' });
    } catch (err) {
      setNotification({ open: true, message: err.message, severity: 'error' });
    }
  };

  const handleRemoveCoupon = async () => {
    try {
      await removeCoupon();
      setNotification({ open: true, message: 'Coupon removed successfully!', severity: 'success' });
    } catch (err) {
      setNotification({ open: true, message: err.message, severity: 'error' });
    }
  };

  const handleCheckout = () => {
    if (!isAuthenticated) {
      navigate('/login?redirect=/checkout');
    } else {
      navigate('/checkout');
    }
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ my: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ my: 4 }}>
        <Alert severity="error">Error loading cart: {error}</Alert>
      </Container>
    );
  }

  if (!cart || !cart.cart_items || cart.cart_items.length === 0) {
    return (
      <Container maxWidth="md" sx={{ my: 4, textAlign: 'center' }}>
        <Typography variant="h5" gutterBottom>Your cart is empty.</Typography>
        <Button variant="contained" color="primary" onClick={() => navigate('/')}>
          Continue Shopping
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ my: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Your Shopping Cart
        </Typography>

        <List>
          {cart.cart_items.map((item) => (
            <React.Fragment key={item.uid}>
              <ListItem
                secondaryAction={
                  <IconButton edge="end" aria-label="delete" onClick={() => handleRemoveItem(item.uid)}>
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemAvatar>
                  {/* ADDED NULL CHECKS HERE */}
                  {item.product_detail && item.product_detail.product_images && item.product_detail.product_images.length > 0 ? (
                    <Avatar
                      variant="square"
                      src={item.product_detail.product_images[0].image}
                      alt={item.product_detail.product_name}
                      sx={{ width: 80, height: 80, mr: 2 }}
                    />
                  ) : (
                    <Avatar variant="square" sx={{ width: 80, height: 80, mr: 2 }}>
                      No Image
                    </Avatar>
                  )}
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Typography variant="h6">
                      {/* ADDED NULL CHECKS HERE */}
                      {item.product_detail ? item.product_detail.product_name : 'Deleted Product'}
                      {item.color_variant_detail && ` (${item.color_variant_detail.color_name})`}
                      {item.size_variant_detail && ` (${item.size_variant_detail.size_name})`}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="body2" color="textSecondary">
                      Price: ${item.product_detail ? parseFloat(item.product_detail.price).toFixed(2) : '0.00'}
                    </Typography>
                  }
                />
                <Box display="flex" alignItems="center">
                  <IconButton
                    onClick={() => handleQuantityChange(item.uid, item.quantity - 1)}
                    disabled={item.quantity <= 1}
                  >
                    <RemoveCircleOutline />
                  </IconButton>
                  <Typography sx={{ mx: 1 }}>{item.quantity}</Typography>
                  <IconButton
                    onClick={() => handleQuantityChange(item.uid, item.quantity + 1)}
                  >
                    <AddCircleOutline />
                  </IconButton>
                  <Typography variant="subtitle1" sx={{ ml: 2 }}>
                    ${parseFloat(item.item_total_price).toFixed(2)}
                  </Typography>
                </Box>
              </ListItem>
              <Divider variant="inset" component="li" />
            </React.Fragment>
          ))}
        </List>

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Subtotal:</Typography>
          <Typography variant="h6">${parseFloat(cart.total_cart_price).toFixed(2)}</Typography>
        </Box>

        {cart.coupon_detail ? (
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'success.main' }}>
            <Typography variant="h6">Coupon ({cart.coupon_detail.coupon_code}):</Typography>
            <Box display="flex" alignItems="center">
              <Typography variant="h6">-${parseFloat(cart.coupon_detail.discount_amount).toFixed(2)}</Typography>
              <Button size="small" onClick={handleRemoveCoupon} sx={{ ml: 1 }}>Remove</Button>
            </Box>
          </Box>
        ) : (
          <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
            <TextField
              label="Coupon Code"
              variant="outlined"
              size="small"
              value={couponCode}
              onChange={(e) => setCouponCode(e.target.value)}
              sx={{ mr: 1 }}
            />
            <Button variant="outlined" onClick={handleApplyCoupon} disabled={!couponCode}>
              Apply Coupon
            </Button>
          </Box>
        )}

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5">Order Total:</Typography>
          <Typography variant="h5">${parseFloat(cart.total_price_after_coupon).toFixed(2)}</Typography>
        </Box>

        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
          <Button variant="contained" color="primary" size="large" onClick={handleCheckout}>
            Proceed to Checkout
          </Button>
        </Box>
      </Paper>
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={() => setNotification({ ...notification, open: false })} severity={notification.severity} sx={{ width: '100%' }}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Cart;