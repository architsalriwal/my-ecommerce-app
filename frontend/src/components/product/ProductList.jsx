// C:\Users\archi\Downloads\Folder2\frontend\src\components\product\ProductList.jsx

import React from 'react';
import { Grid } from '@mui/material';
import ProductCard from './ProductCard';

const ProductList = ({ products }) => {
  return (
    <Grid container spacing={3}>
      {/* Changed product.id to product.uid based on your BaseModel */}
      {products.map((product) => (
        <Grid key={product.uid} xs={12} sm={6} md={4} lg={3}> {/* Removed 'item' prop */}
          <ProductCard product={product} />
        </Grid>
      ))}
    </Grid>
  );
};

export default ProductList;