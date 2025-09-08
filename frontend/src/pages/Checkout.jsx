import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  Box,
  Paper,
  CircularProgress,
  Alert,
  Snackbar,
  Grid,
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField,
  FormControl,
  FormLabel,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Divider,
} from '@mui/material';
import { AddCircleOutline, Edit, Delete } from '@mui/icons-material';
// FIX: Import the custom API instance that handles authentication
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';

import { Elements } from '@stripe/react-stripe-js';
import StripePaymentForm from '../components/StripePaymentForm';

const validateAddressForm = (address) => {
  const errors = {};
  if (!address.full_name) errors.full_name = "Full Name is required";
  if (!address.address_line1) errors.address_line1 = "Address Line 1 is required";
  if (!address.city) errors.city = "City is required";
  if (!address.state) errors.state = "State is required";
  if (!address.postal_code) errors.postal_code = "Postal Code is required";
  if (!address.country) errors.country = "Country is required";
  if (!address.phone_number) errors.phone_number = "Phone Number is required";
  return errors;
};


const steps = ['Shipping Address', 'Payment Method', 'Review & Place Order'];

const Checkout = ({ stripe }) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  // We're now using fetchCart from the context to re-sync
  const { cart, fetchCart } = useCart();

  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [shippingAddresses, setShippingAddresses] = useState([]);
  const [selectedAddressUid, setSelectedAddressUid] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('COD');
  const [newAddressForm, setNewAddressForm] = useState({
    full_name: '', address_line1: '', address_line2: '', city: '',
    state: '', postal_code: '', country: '', phone_number: '', is_default: false
  });
  const [addressFormErrors, setAddressFormErrors] = useState({});
  const [editingAddressUid, setEditingAddressUid] = useState(null);
  const [showNewAddressForm, setShowNewAddressForm] = useState(false);

  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [clientSecret, setClientSecret] = useState(null);
  const [currentOrderUid, setCurrentOrderUid] = useState(null);
  const [stripeFormLoading, setStripeFormLoading] = useState(false);

  console.log('Checkout.jsx: stripe prop received:', stripe);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login?redirect=/checkout');
    } else {
      // FIX: Force a re-fetch of the cart and addresses on component load
      // This ensures we always have the latest cart data from the backend
      const fetchData = async () => {
        setLoading(true);
        await Promise.all([
          fetchShippingAddresses(),
          fetchCart(),
        ]);
        setLoading(false);
      };
      fetchData();
    }
  }, [isAuthenticated, navigate, fetchCart]);

  useEffect(() => {
    // We moved the loading state check inside the first useEffect to ensure it waits for the cart fetch.
    // This hook now only runs after the initial load.
    if (!loading && isAuthenticated && (!cart || !cart.cart_items || cart.cart_items.length === 0)) {
      setNotification({ open: true, message: 'Your cart is empty. Please add items before checkout.', severity: 'warning' });
      navigate('/cart');
    }
  }, [loading, isAuthenticated, cart, navigate]);

  const fetchShippingAddresses = async () => {
    try {
      // FIX: Changed from axios to the authenticated api instance
      const response = await api.get('/home/shipping-addresses/');
      setShippingAddresses(response.data);
      const defaultAddress = response.data.find(addr => addr.is_default);
      if (defaultAddress) {
        setSelectedAddressUid(defaultAddress.uid);
      } else if (response.data.length > 0) {
        setSelectedAddressUid(response.data[0].uid);
      }
    } catch (error) {
      console.error('Error fetching shipping addresses:', error);
      setNotification({ open: true, message: 'Failed to fetch shipping addresses.', severity: 'error' });
    }
  };

  const handleNewAddressChange = (e) => {
    setNewAddressForm({ ...newAddressForm, [e.target.name]: e.target.value });
  };

  const handleAddOrUpdateAddress = async () => {
    const errors = validateAddressForm(newAddressForm);
    if (Object.keys(errors).length > 0) {
      setAddressFormErrors(errors);
      setNotification({ open: true, message: 'Please correct the form errors.', severity: 'error' });
      return;
    }
    setLoading(true);
    try {
      if (editingAddressUid) {
        // FIX: Changed from axios to the authenticated api instance
        await api.put(`/home/shipping-addresses/${editingAddressUid}/`, newAddressForm);
        setNotification({ open: true, message: 'Address updated successfully!', severity: 'success' });
      } else {
        // FIX: Changed from axios to the authenticated api instance
        const response = await api.post('/home/shipping-addresses/', newAddressForm);
        setNotification({ open: true, message: 'Address added successfully!', severity: 'success' });
        setSelectedAddressUid(response.data.uid);
      }
      setShowNewAddressForm(false);
      setEditingAddressUid(null);
      setNewAddressForm({
        full_name: '', address_line1: '', address_line2: '', city: '',
        state: '', postal_code: '', country: '', phone_number: '', is_default: false
      });
      setAddressFormErrors({});
      fetchShippingAddresses();
    } catch (error) {
      console.error('Error adding/updating address:', error);
      setNotification({ open: true, message: `Failed to save address: ${error.response?.data?.detail || error.message}`, severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleEditAddress = (address) => {
    setNewAddressForm(address);
    setEditingAddressUid(address.uid);
    setShowNewAddressForm(true);
    setAddressFormErrors({});
  };

  const handleDeleteAddress = async (addressUid) => {
    setLoading(true);
    try {
      // FIX: Changed from axios to the authenticated api instance
      await api.delete(`/home/shipping-addresses/${addressUid}/`);
      setNotification({ open: true, message: 'Address deleted successfully!', severity: 'success' });
      fetchShippingAddresses();
      if (selectedAddressUid === addressUid) {
        setSelectedAddressUid(null);
      }
    } catch (error) {
      console.error('Error deleting address:', error);
      setNotification({ open: true, message: `Failed to delete address: ${error.response?.data?.detail || error.message}`, severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleSetDefaultAddress = async (addressUid) => {
    setLoading(true);
    try {
      // FIX: Changed from axios to the authenticated api instance
      await api.post('/home/shipping-addresses/set-default/', { uid: addressUid });
      setNotification({ open: true, message: 'Default address set!', severity: 'success' });
      fetchShippingAddresses();
    } catch (error) {
      console.error('Error setting default address:', error);
      setNotification({ open: true, message: `Failed to set default address: ${error.response?.data?.detail || error.message}`, severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (activeStep === 0) {
      if (!selectedAddressUid && !showNewAddressForm) {
        setNotification({ open: true, message: 'Please select or add a shipping address.', severity: 'warning' });
        return;
      }
      if (showNewAddressForm) {
        const errors = validateAddressForm(newAddressForm);
        if (Object.keys(errors).length > 0) {
          setAddressFormErrors(errors);
          setNotification({ open: true, message: 'Please complete the new address form.', severity: 'error' });
          return;
        }
        if (!editingAddressUid) {
          await handleAddOrUpdateAddress(); // Ensure address is saved before proceeding
          if (Object.keys(addressFormErrors).length > 0) return; // If save failed, stop
        }
      }
    }

    if (activeStep === 1 && paymentMethod === 'STRIPE') {
      setStripeFormLoading(true);
      try {
        if (!cart || !cart.uid) {
          // FIX: Add a specific check and throw here
          throw new Error("Cart is not loaded or has no UID. Please refresh the page and try again.");
        }
        if (!selectedAddressUid) {
          throw new Error("No shipping address selected.");
        }

        console.log('Checkout.jsx: Attempting to fetch client secret...');
        // FIX: The backend is returning cart.uid as an array, but it expects a string.
        // We safely check if cart.uid is an array and take the first element.
        const orderCreationResponse = await api.post('/home/orders/create_payment_intent/', {
          cart_uid: Array.isArray(cart.uid) ? cart.uid[0] : cart.uid,
          shipping_address_uid: selectedAddressUid,
          payment_method: 'STRIPE',
        });
        setClientSecret(orderCreationResponse.data.client_secret);
        setCurrentOrderUid(orderCreationResponse.data.order_uid);
        console.log("Checkout.jsx: Fetched clientSecret and Order UID successfully.");
      } catch (error) {
        console.error('Checkout.jsx: Error fetching client secret:', error.response?.data || error.message);
        setNotification({ open: true, message: `Failed to initialize Stripe payment: ${error.response?.data?.detail || error.message}`, severity: 'error' });
        setStripeFormLoading(false);
        return;
      } finally {
        setStripeFormLoading(false);
      }
    }
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const onPaymentSuccess = (orderUid) => {
    fetchCart();
    navigate(`/order-success/${orderUid}`);
  };

  const onPaymentFailure = (error) => {
    setNotification({ open: true, message: `Payment failed: ${error.message || 'An error occurred.'}`, severity: 'error' });
  };

  const handlePlaceOrderCOD = async () => {
    setLoading(true);
    try {
      const orderData = {
        cart_uid: cart.uid,
        shipping_address_uid: selectedAddressUid,
        payment_method: 'COD',
      };
      // FIX: Changed from axios to the authenticated api instance
      const response = await api.post('/home/orders/', orderData);
      setNotification({ open: true, message: 'Order placed successfully!', severity: 'success' });
      onPaymentSuccess(response.data.uid);
    } catch (error) {
      console.error('Error placing COD order:', error.response?.data || error.message);
      let errorMessage = 'Failed to place COD order. Please try again.';
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data.non_field_errors) {
          errorMessage = error.response.data.non_field_errors[0];
        } else if (error.response.data.product_uid) {
          errorMessage = `Product error: ${error.response.data.product_uid}`;
        } else if (error.response.data.shipping_address_uid) {
          errorMessage = `Shipping address error: ${error.response.data.shipping_address_uid}`;
        } else if (error.response.data.payment_method) {
          errorMessage = `Payment method error: ${error.response.data.payment_method}`;
        } else if (error.response.data.cart_items) {
          errorMessage = `Cart item error: ${error.response.data.cart_items[0]}`;
        }
      }
      setNotification({ open: true, message: errorMessage, severity: 'error' });
    } finally {
      setLoading(false);
    }
  };


  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>Select Shipping Address</Typography>
            {loading ? (
              <Box display="flex" justifyContent="center"><CircularProgress /></Box>
            ) : shippingAddresses.length === 0 && !showNewAddressForm ? (
                <Alert severity="info">No addresses found. Please add a new one.</Alert>
            ) : (
              <List>
                {shippingAddresses.map((address) => (
                  <Paper key={address.uid} elevation={2} sx={{ mb: 2, p: 2 }}>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <FormControlLabel
                        value={address.uid}
                        control={<Radio checked={selectedAddressUid === address.uid} onChange={() => setSelectedAddressUid(address.uid)} />}
                        label={
                          <Typography variant="body1">
                            {address.full_name}, {address.address_line1}{address.address_line2 && `, ${address.address_line2}`}<br />
                            {address.city}, {address.state} - {address.postal_code}<br />
                            {address.country}<br />
                            Phone: {address.phone_number}
                          </Typography>
                        }
                      />
                      <Box>
                        {!address.is_default && (
                            <Button size="small" onClick={() => handleSetDefaultAddress(address.uid)}>Set Default</Button>
                        )}
                        <IconButton onClick={() => handleEditAddress(address)} color="primary">
                          <Edit />
                        </IconButton>
                        <IconButton onClick={() => handleDeleteAddress(address.uid)} color="error">
                          <Delete />
                        </IconButton>
                      </Box>
                    </Box>
                  </Paper>
                ))}
              </List>
            )}

            <Button
              variant="outlined"
              startIcon={<AddCircleOutline />}
              onClick={() => {
                setShowNewAddressForm(!showNewAddressForm);
                setEditingAddressUid(null);
                setNewAddressForm({
                  full_name: '', address_line1: '', address_line2: '', city: '',
                  state: '', postal_code: '', country: '', phone_number: '', is_default: false
                });
                setAddressFormErrors({});
              }}
              sx={{ mt: 2 }}
            >
              {showNewAddressForm ? 'Cancel Add/Edit Address' : 'Add New Address'}
            </Button>

            {showNewAddressForm && (
              <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
                <Typography variant="h6" gutterBottom>{editingAddressUid ? 'Edit Address' : 'Add New Address'}</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Full Name"
                      name="full_name"
                      value={newAddressForm.full_name}
                      onChange={handleNewAddressChange}
                      error={!!addressFormErrors.full_name}
                      helperText={addressFormErrors.full_name}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Phone Number"
                      name="phone_number"
                      value={newAddressForm.phone_number}
                      onChange={handleNewAddressChange}
                      error={!!addressFormErrors.phone_number}
                      helperText={addressFormErrors.phone_number}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Address Line 1"
                      name="address_line1"
                      value={newAddressForm.address_line1}
                      onChange={handleNewAddressChange}
                      error={!!addressFormErrors.address_line1}
                      helperText={addressFormErrors.address_line1}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Address Line 2 (Optional)"
                      name="address_line2"
                      value={newAddressForm.address_line2}
                      onChange={handleNewAddressChange}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="City"
                      name="city"
                      value={newAddressForm.city}
                      onChange={handleNewAddressChange}
                      error={!!addressFormErrors.city}
                      helperText={addressFormErrors.city}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="State"
                      name="state"
                      value={newAddressForm.state}
                      onChange={handleNewAddressChange}
                      error={!!addressFormErrors.state}
                      helperText={addressFormErrors.state}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Postal Code"
                      name="postal_code"
                      value={newAddressForm.postal_code}
                      onChange={handleNewAddressChange}
                      error={!!addressFormErrors.postal_code}
                      helperText={addressFormErrors.postal_code}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Country"
                      name="country"
                      value={newAddressForm.country}
                      onChange={handleNewAddressChange}
                      error={!!addressFormErrors.country}
                      helperText={addressFormErrors.country}
                    />
                  </Grid>
                  <Grid item xs={12}>
                      <FormControlLabel
                          control={
                              <input
                                  type="checkbox"
                                  name="is_default"
                                  checked={newAddressForm.is_default}
                                  onChange={(e) => setNewAddressForm({ ...newAddressForm, is_default: e.target.checked })}
                              />
                          }
                          label="Set as Default Address"
                      />
                  </Grid>
                  <Grid item xs={12}>
                    <Button variant="contained" color="primary" onClick={handleAddOrUpdateAddress} disabled={loading}>
                      {loading ? <CircularProgress size={24} /> : (editingAddressUid ? 'Update Address' : 'Save Address')}
                    </Button>
                  </Grid>
                </Grid>
              </Paper>
            )}
          </Box>
        );

      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>Select Payment Method</Typography>
            <FormControl component="fieldset">
              <FormLabel component="legend">Choose an Option</FormLabel>
              <RadioGroup
                aria-label="payment method"
                name="paymentMethod"
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
              >
                <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
                  <FormControlLabel value="COD" control={<Radio />} label="Cash on Delivery (COD)" />
                </Paper>
                <Paper elevation={2} sx={{ p: 2 }}>
                  <FormControlLabel value="STRIPE" control={<Radio />} label="Pay with Card (Stripe)" />
                  <Typography variant="caption" color="textSecondary" sx={{ ml: 4 }}>
                    (Card payments are processed securely by Stripe.)
                  </Typography>
                </Paper>
              </RadioGroup>
            </FormControl>
          </Box>
        );

      case 2:
        const selectedAddress = shippingAddresses.find(addr => addr.uid === selectedAddressUid);
        return (
          <Box>
            <Typography variant="h6" gutterBottom>Review Your Order</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper elevation={2} sx={{ p: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>Shipping Address:</Typography>
                  {selectedAddress ? (
                    <Typography>
                      {selectedAddress.full_name}<br />
                      {selectedAddress.address_line1}{selectedAddress.address_line2 && `, ${selectedAddress.address_line2}`}<br />
                      {selectedAddress.city}, {selectedAddress.state} - {selectedAddress.postal_code}<br />
                      {selectedAddress.country}<br />
                      Phone: {selectedAddress.phone_number}
                    </Typography>
                  ) : (
                    <Alert severity="warning">No shipping address selected.</Alert>
                  )}
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper elevation={2} sx={{ p: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>Payment Method:</Typography>
                  <Typography>{paymentMethod === 'COD' ? 'Cash on Delivery' : 'Pay with Card (Stripe)'}</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12}>
                <Paper elevation={2} sx={{ p: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>Order Summary:</Typography>
                  {!cart || !cart.cart_items || cart.cart_items.length === 0 ? (
                    <Alert severity="warning">Your cart is empty.</Alert>
                  ) : (
                    <List disablePadding>
                      {cart.cart_items.map((item) => (
                        <ListItem key={item.uid} sx={{ py: 1, px: 0 }}>
                          <ListItemText
                            primary={`${item.product_detail.product_name} (${item.color_variant_detail?.color_name || ''} ${item.size_variant_detail?.size_name || ''}) x ${item.quantity}`}
                            secondary={`Price: $${parseFloat(item.product_detail.price).toFixed(2)}`}
                          />
                          <Typography variant="body2">${parseFloat(item.item_total_price).toFixed(2)}</Typography>
                        </ListItem>
                      ))}
                      <Divider sx={{ my: 1 }} />
                      <ListItem sx={{ py: 1, px: 0 }}>
                        <ListItemText primary="Total Items" />
                        <Typography variant="subtitle1">{cart.total_cart_items}</Typography>
                      </ListItem>
                      <ListItem sx={{ py: 1, px: 0 }}>
                        <ListItemText primary="Subtotal" />
                        <Typography variant="subtitle1">${parseFloat(cart.total_cart_price).toFixed(2)}</Typography>
                      </ListItem>
                      {cart.coupon_detail && (
                        <ListItem sx={{ py: 1, px: 0 }}>
                          <ListItemText primary={`Coupon: ${cart.coupon_detail.coupon_code}`} />
                          <Typography variant="subtitle1" color="success">-${parseFloat(cart.coupon_detail.discount_amount).toFixed(2)}</Typography>
                        </ListItem>
                      )}
                      <ListItem sx={{ py: 1, px: 0 }}>
                        <ListItemText primary="Shipping" />
                        <Typography variant="subtitle1">$0.00</Typography>
                      </ListItem>
                      <ListItem sx={{ py: 1, px: 0 }}>
                        <ListItemText primary="Order Total" />
                        <Typography variant="h6">${parseFloat(cart.total_price_after_coupon).toFixed(2)}</Typography>
                      </ListItem>
                    </List>
                  )}
                </Paper>
              </Grid>
            </Grid>

            {/* Conditional rendering of Elements and StripePaymentForm */}
            {paymentMethod === 'STRIPE' && stripe && clientSecret ? (
              <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
                <Typography variant="h6" gutterBottom>Enter Payment Details</Typography>
                {/* Elements provider now wraps StripePaymentForm and receives clientSecret */}
                <Elements stripe={stripe} options={{ clientSecret: clientSecret }}>
                  <StripePaymentForm
                    orderData={{
                      cart_uid: cart.uid,
                      shipping_address_uid: selectedAddressUid,
                      order_uid: currentOrderUid,
                    }}
                    onPaymentSuccess={onPaymentSuccess}
                    onPaymentFailure={onPaymentFailure}
                  />
                </Elements>
              </Paper>
            ) : paymentMethod === 'STRIPE' && stripeFormLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Initializing Stripe...</Typography>
              </Box>
            ) : paymentMethod === 'STRIPE' && !stripe ? (
              <Alert severity="warning" sx={{ mt: 3 }}>Stripe is not yet loaded. Please wait or refresh.</Alert>
            ) : (
              <Button
                variant="contained"
                color="primary"
                onClick={handlePlaceOrderCOD}
                disabled={loading || !selectedAddressUid || !cart || cart.cart_items.length === 0}
                sx={{ mt: 3 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Place Order (COD)'}
              </Button>
            )}
          </Box>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Container maxWidth="md" sx={{ my: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Checkout
        </Typography>
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box>
          {activeStep === steps.length ? (
            <Box textAlign="center">
              <Typography variant="h5" gutterBottom>Thank you for your order!</Typography>
              <Typography variant="body1">
                Your order has been placed successfully. You will receive an email confirmation shortly.
              </Typography>
              <Button onClick={() => navigate('/orders')} sx={{ mt: 3 }}>
                View My Orders
              </Button>
            </Box>
          ) : (
            <>
              {getStepContent(activeStep)}
              {!(activeStep === steps.length - 1 && paymentMethod === 'STRIPE') && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
                  {activeStep !== 0 && (
                    <Button onClick={handleBack} sx={{ mr: 1 }}>
                      Back
                    </Button>
                  )}
                  {activeStep === steps.length - 1 ? (
                    paymentMethod === 'COD' && (
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={handlePlaceOrderCOD}
                            disabled={loading || !selectedAddressUid || !cart || cart.cart_items.length === 0}
                        >
                            {loading ? <CircularProgress size={24} /> : 'Place Order (COD)'}
                        </Button>
                    )
                  ) : (
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleNext}
                      disabled={loading || (activeStep === 0 && (!selectedAddressUid && shippingAddresses.length > 0 && !showNewAddressForm))}
                    >
                      Next
                    </Button>
                  )}
                </Box>
              )}
            </>
          )}
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

export default Checkout;
