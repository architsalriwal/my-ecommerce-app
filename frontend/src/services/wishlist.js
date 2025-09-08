// C:\Users\archi\Downloads\Folder2\frontend\src\services\wishlist.js

import axios from 'axios';

const API_URL = '/api/wishlist/';

export const wishlistService = {
    // Get all wishlist items
    getWishlist: async() => {
        try {
            const response = await axios.get(API_URL);
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // Add item to wishlist
    addToWishlist: async(productId, size) => {
        try {
            const response = await axios.post(`${API_URL}add/${productId}/`, { size });
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // Remove item from wishlist
    removeFromWishlist: async(productId, size) => {
        try {
            const response = await axios.delete(`${API_URL}remove/${productId}/`, {
                params: { size }
            });
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // Move item from wishlist to cart
    moveToCart: async(productId) => {
        try {
            const response = await axios.post(`${API_URL}move_to_cart/${productId}/`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }
};