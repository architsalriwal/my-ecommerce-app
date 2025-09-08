// C:\Users\archi\Downloads\Folder2\frontend\src\pages\Wishlist.jsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const Wishlist = () => {
  const [wishlistItems, setWishlistItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Fetch wishlist items when component mounts
  useEffect(() => {
    fetchWishlistItems();
  }, []);

  const fetchWishlistItems = async () => {
    try {
      const response = await axios.get('/api/wishlist/');
      setWishlistItems(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching wishlist:', error);
      toast.error('Failed to load wishlist items');
      setLoading(false);
    }
  };

  const removeFromWishlist = async (productId, sizeVariant) => {
    try {
      await axios.delete(`/api/wishlist/remove/${productId}/`, {
        params: { size: sizeVariant }
      });
      toast.success('Item removed from wishlist');
      // Refresh wishlist items
      fetchWishlistItems();
    } catch (error) {
      console.error('Error removing from wishlist:', error);
      toast.error('Failed to remove item from wishlist');
    }
  };

  const moveToCart = async (productId) => {
    try {
      await axios.post(`/api/wishlist/move_to_cart/${productId}/`);
      toast.success('Item moved to cart successfully');
      // Refresh wishlist items
      fetchWishlistItems();
      // Optionally navigate to cart
      navigate('/cart');
    } catch (error) {
      console.error('Error moving to cart:', error);
      toast.error('Failed to move item to cart');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">My Wishlist</h1>
      
      {wishlistItems.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500 text-lg">Your wishlist is empty</p>
          <button 
            onClick={() => navigate('/')}
            className="mt-4 px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Continue Shopping
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {wishlistItems.map((item) => (
            <div key={item.uid} className="border rounded-lg overflow-hidden shadow-lg">
              <img 
                src={item.product.product_images[0]?.image || '/placeholder.jpg'} 
                alt={item.product.product_name}
                className="w-full h-48 object-cover"
              />
              <div className="p-4">
                <h2 className="text-xl font-semibold mb-2">{item.product.product_name}</h2>
                <p className="text-gray-600 mb-2">Size: {item.size_variant?.size_name}</p>
                <p className="text-lg font-bold mb-4">
                  ${item.product.price + (item.size_variant?.price || 0)}
                </p>
                
                <div className="flex justify-between">
                  <button
                    onClick={() => moveToCart(item.product.uid)}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    Move to Cart
                  </button>
                  <button
                    onClick={() => removeFromWishlist(item.product.uid, item.size_variant?.size_name)}
                    className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                  >
                    Remove
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Wishlist;