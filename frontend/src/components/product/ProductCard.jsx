// C:\Users\archi\Downloads\Folder2\frontend\src\components\product\ProductCard.jsx

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardMedia, Typography, Button, Box } from '@mui/material';
import { useCart } from '../../context/CartContext';

const ProductCard = ({ product }) => {
  const navigate = useNavigate();
  const { addToCart } = useCart();

  const handleAddToCart = async (e) => {
    e.stopPropagation(); // Prevent the card's onClick from firing when button is clicked
    try {
      // Pass product.uid and default quantity, with null for variants
      await addToCart(product.uid, 1, null, null); // Pass null for color/size variants
      // Optionally add a success notification here
      console.log('Product added to cart from card:', product.product_name);
    } catch (error) {
      console.error('Error adding to cart from card:', error);
      // Optionally add an error notification here
    }
  };

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        cursor: 'pointer',
      }}
      onClick={() => navigate(`/products/${product.uid}`)}
    >
      {product.product_images && product.product_images.length > 0 ? (
        <CardMedia
          component="img"
          height="200"
          image={product.product_images[0].image_url}
          alt={product.product_name}
          sx={{ objectFit: 'contain' }}
        />
      ) : (
        <Box
          sx={{
            height: '200px',
            backgroundColor: '#e0e0e0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#888',
            textAlign: 'center',
          }}
        >
          <Typography variant="caption">No Image Available</Typography>
        </Box>
      )}

      <CardContent sx={{ flexGrow: 1 }}>
        <Typography gutterBottom variant="h6" component="div">
          {product.product_name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          ${product.price}
        </Typography>
      </CardContent>
      <Button
        variant="contained"
        color="primary"
        onClick={handleAddToCart}
        sx={{ m: 1 }}
      >
        Add to Cart
      </Button>
    </Card>
  );
};

export default ProductCard;