// C:\Users\archi\Downloads\Folder2\frontend\src\components\product\ProductDetail.jsx

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import {
  Container,
  Grid,
  Typography,
  Button,
  Box,
  Paper,
  Rating,
  TextField,
  Snackbar,
  Alert,
  ToggleButtonGroup, // Added for variant selection
  ToggleButton,      // Added for variant selection
} from '@mui/material';
import axios from 'axios';

const ProductDetail = () => {
  const { id: productSlug } = useParams();
  const { addToCart } = useCart();
  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [selectedColor, setSelectedColor] = useState(null);
  const [selectedSize, setSelectedSize] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '' });

  useEffect(() => {
    fetchProduct();
  }, [productSlug]);

  const fetchProduct = async () => {
    try {
      const response = await axios.get(`/api/products/${productSlug}/`);
      setProduct(response.data);
      // Auto-select first variant if available
      if (response.data.color_variant && response.data.color_variant.length > 0) {
        setSelectedColor(response.data.color_variant[0].uid);
      }
      if (response.data.size_variant && response.data.size_variant.length > 0) {
        setSelectedSize(response.data.size_variant[0].uid);
      }
    } catch (error) {
      console.error('Error fetching product:', error);
    } finally {
      // setLoading(false); // No loading state for ProductDetail here, but good practice
    }
  };

  const handleAddToCart = async () => {
    if (!selectedColor && product.color_variant && product.color_variant.length > 0) {
      setNotification({ open: true, message: 'Please select a color variant!', severity: 'warning' });
      return;
    }
    if (!selectedSize && product.size_variant && product.size_variant.length > 0) {
      setNotification({ open: true, message: 'Please select a size variant!', severity: 'warning' });
      return;
    }

    try {
      await addToCart(product.uid, quantity, selectedColor, selectedSize);
      setNotification({
        open: true,
        message: 'Product added to cart successfully!',
        severity: 'success',
      });
    } catch (error) {
      setNotification({
        open: true,
        message: `Error adding product to cart: ${error.response?.data?.detail || error.message}`,
        severity: 'error',
      });
    }
  };

  const handleColorChange = (event, newColor) => {
    setSelectedColor(newColor);
  };

  const handleSizeChange = (event, newSize) => {
    setSelectedSize(newSize);
  };

  if (!product) {
    return <Typography>Loading...</Typography>;
  }

  // Calculate dynamic price based on selected variants (frontend display only)
  // Ensure product.price is parsed to a float
  let currentPrice = parseFloat(product.price); 
  const selectedColorObj = product.color_variant.find(cv => cv.uid === selectedColor);
  const selectedSizeObj = product.size_variant.find(sv => sv.uid === selectedSize);

  if (selectedColorObj) {
    // Ensure selectedColorObj.price is parsed to a float
    currentPrice += parseFloat(selectedColorObj.price); 
  }
  if (selectedSizeObj) {
    // Ensure selectedSizeObj.price is parsed to a float
    currentPrice += parseFloat(selectedSizeObj.price); 
  }


  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Paper elevation={3}>
            {product.product_images && product.product_images.length > 0 ? (
              <img
                src={product.product_images[0].image_url}
                alt={product.product_name}
                style={{ width: '100%', height: 'auto', display: 'block' }}
              />
            ) : (
              <Box
                sx={{
                  width: '100%',
                  height: 'auto',
                  minHeight: '300px',
                  backgroundColor: '#f0f0f0',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#aaa',
                  textAlign: 'center',
                }}
              >
                <Typography variant="body2">No image available</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="h4" gutterBottom>
            {product.product_name}
          </Typography>
          <Rating value={product.average_rating} readOnly precision={0.1} />
          <Typography variant="h5" color="primary" sx={{ my: 2 }}>
            {/* currentPrice is already a float due to conversions above */}
            ${currentPrice.toFixed(2)}
          </Typography>
          <Typography variant="body1" paragraph>
            {product.product_desription}
          </Typography>

          {/* Color Variant Selection */}
          {product.color_variant && product.color_variant.length > 0 && (
            <Box sx={{ my: 2 }}>
              <Typography variant="subtitle1" gutterBottom>Color:</Typography>
              <ToggleButtonGroup
                value={selectedColor}
                exclusive
                onChange={handleColorChange}
                aria-label="product color"
                size="small"
              >
                {product.color_variant.map((color) => (
                  <ToggleButton key={color.uid} value={color.uid} aria-label={color.color_name}>
                    {color.color_name}
                  </ToggleButton>
                ))}
              </ToggleButtonGroup>
            </Box>
          )}

          {/* Size Variant Selection */}
          {product.size_variant && product.size_variant.length > 0 && (
            <Box sx={{ my: 2 }}>
              <Typography variant="subtitle1" gutterBottom>Size:</Typography>
              <ToggleButtonGroup
                value={selectedSize}
                exclusive
                onChange={handleSizeChange}
                aria-label="product size"
                size="small"
              >
                {product.size_variant.map((size) => (
                  <ToggleButton key={size.uid} value={size.uid} aria-label={size.size_name}>
                    {size.size_name}
                  </ToggleButton>
                ))}
              </ToggleButtonGroup>
            </Box>
          )}

          <Box sx={{ my: 2 }}>
            <TextField
              type="number"
              label="Quantity"
              value={quantity}
              onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
              inputProps={{ min: 1 }}
              sx={{ width: 100, mr: 2 }}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleAddToCart}
            >
              Add to Cart
            </Button>
          </Box>
        </Grid>
      </Grid>
      <Snackbar
        open={notification.open}
        autoHideDuration={3000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity || "success"} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default ProductDetail;