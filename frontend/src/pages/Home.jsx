// C:\Users\archi\Downloads\Folder2\frontend\src\pages\Home.jsx

import React, { useState, useEffect } from 'react';
import { Container, Typography, Grid, CircularProgress, Alert } from '@mui/material'; // Added CircularProgress, Alert
import ProductList from '../components/product/ProductList';
import axios from 'axios'; // Using axios directly, assuming global config from index.js

const Home = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try { 
      const response = await axios.get('/api/products/products/'); // Adjusted API path based on your api_urls setup
      // Check if the response data has a 'results' key (indicating pagination)
      if (response.data && Array.isArray(response.data.results)) {
        setProducts(response.data.results);
      } else if (response.data && Array.isArray(response.data)) {
        // Fallback for non-paginated lists if applicable (though less likely the current issue)
        setProducts(response.data);
      } else {
        // If response.data is neither an array nor an object with 'results' array
        console.error("Unexpected API response structure:", response.data);
        setError('Failed to fetch products: Unexpected data format.');
        setProducts([]); // Ensure products remains an array
      }
    } catch (err) {
      setError('Failed to fetch products. Please try again later.');
      console.error('Error fetching products:', err.response?.data || err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading products...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  // Display a message if no products are found after loading
  if (products.length === 0) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="info">No products found at the moment.</Alert>
      </Container>
    );
  }

  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Featured Products
      </Typography>
      <ProductList products={products} />
    </Container>
  );
};

export default Home;