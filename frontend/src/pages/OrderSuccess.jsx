// C:\Users\archi\Downloads\Folder2\frontend\src\pages\OrderSuccess.jsx

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Paper,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  Alert,
} from '@mui/material';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';

// Removed useStripe and useElements imports as they are not needed here.
// import { useStripe, useElements } from '@stripe/react-stripe-js'; // REMOVED

const OrderSuccess = () => {
  const { orderUid } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { fetchCart } = useCart(); // To clear cart after successful order

  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Removed direct useStripe/useElements calls from here
  // const stripe = useStripe(); // REMOVED
  // const elements = useElements(); // REMOVED

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login'); // Redirect to login if not authenticated
      return;
    }

    const fetchOrderDetails = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get(`/api/home/orders/${orderUid}/`);
        setOrder(response.data);
        fetchCart(); // Clear the cart after order is successfully viewed
      } catch (err) {
        console.error('Error fetching order details:', err);
        setError('Failed to load order details. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    if (orderUid) {
      fetchOrderDetails();
    } else {
      setError('No order ID provided.');
      setLoading(false);
    }
  }, [orderUid, isAuthenticated, navigate, fetchCart]);

  if (loading) {
    return (
      <Container maxWidth="sm" sx={{ my: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading order details...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="sm" sx={{ my: 4, textAlign: 'center' }}>
        <Alert severity="error">{error}</Alert>
        <Button variant="contained" sx={{ mt: 2 }} onClick={() => navigate('/')}>
          Go to Home
        </Button>
      </Container>
    );
  }

  if (!order) {
    return (
      <Container maxWidth="sm" sx={{ my: 4, textAlign: 'center' }}>
        <Alert severity="info">Order not found.</Alert>
        <Button variant="contained" sx={{ mt: 2 }} onClick={() => navigate('/')}>
          Go to Home
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ my: 4 }}>
      <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h4" color="success" gutterBottom>
          Order Placed Successfully!
        </Typography>
        <Typography variant="body1" sx={{ mb: 2 }}>
          Thank you for your purchase. Your order details are below.
        </Typography>

        <Box sx={{ my: 3, textAlign: 'left' }}>
          <Typography variant="h6" gutterBottom>Order Summary</Typography>
          <List disablePadding>
            <ListItem>
              <ListItemText primary="Order ID" />
              <Typography variant="subtitle1">{order.uid}</Typography>
            </ListItem>
            <ListItem>
              <ListItemText primary="Order Status" />
              <Typography variant="subtitle1">{order.status}</Typography>
            </ListItem>
            <ListItem>
              <ListItemText primary="Payment Method" />
              <Typography variant="subtitle1">{order.payment_method}</Typography>
            </ListItem>
            <ListItem>
              <ListItemText primary="Payment Status" />
              <Typography variant="subtitle1">{order.payment_status}</Typography>
            </ListItem>
            <ListItem>
              <ListItemText primary="Order Date" />
              <Typography variant="subtitle1">{new Date(order.created_at).toLocaleDateString()}</Typography>
            </ListItem>
            <Divider sx={{ my: 1 }} />
            {order.order_items.map((item) => (
              <ListItem key={item.uid}>
                <ListItemText
                  primary={`${item.product_name} (${item.color_name || ''} ${item.size_name || ''}) x ${item.quantity}`}
                  secondary={`Price at purchase: $${parseFloat(item.price_at_purchase).toFixed(2)}`}
                />
                <Typography variant="body2">${(parseFloat(item.price_at_purchase) * item.quantity).toFixed(2)}</Typography>
              </ListItem>
            ))}
            <Divider sx={{ my: 1 }} />
            <ListItem>
              <ListItemText primary="Total Amount" />
              <Typography variant="h6">${parseFloat(order.total_amount).toFixed(2)}</Typography>
            </ListItem>
          </List>
        </Box>

        <Box sx={{ my: 3, textAlign: 'left' }}>
          <Typography variant="h6" gutterBottom>Shipping Address</Typography>
          {order.shipping_address_detail ? (
            <Typography>
              {order.shipping_address_detail.full_name}<br />
              {order.shipping_address_detail.address_line1}{order.shipping_address_detail.address_line2 && `, ${order.shipping_address_detail.address_line2}`}<br />
              {order.shipping_address_detail.city}, {order.shipping_address_detail.state} - {order.shipping_address_detail.postal_code}<br />
              {order.shipping_address_detail.country}<br />
              Phone: {order.shipping_address_detail.phone_number}
            </Typography>
          ) : (
            <Typography>No shipping address provided.</Typography>
          )}
        </Box>

        <Button variant="contained" color="primary" onClick={() => navigate('/orders')} sx={{ mt: 3, mr: 2 }}>
          View All Orders
        </Button>
        <Button variant="outlined" onClick={() => navigate('/')} sx={{ mt: 3 }}>
          Continue Shopping
        </Button>
      </Paper>
    </Container>
  );
};

export default OrderSuccess;