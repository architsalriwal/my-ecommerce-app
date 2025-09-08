import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import axios from 'axios';
import AuthService from '../services/auth.js';

const api = axios.create({
    baseURL: '/',
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

const CartContext = createContext(null);

export const CartProvider = ({ children }) => {
    const [cart, setCart] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchCart = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.get('/api/cart/');
            setCart(response.data);

            if (response.data && response.data.uid) {
                localStorage.setItem('cart_uid', response.data.uid);
                console.log("CartContext: Saved cart UID to localStorage:", response.data.uid);
            } else {
                localStorage.removeItem('cart_uid');
                console.log("CartContext: No cart UID found, removing from localStorage.");
            }
        } catch (err) {
            console.error('Error fetching cart:', err.response ? err.response.data : err.message);
            setCart({});
            setError(err.response?.data?.detail || err.message || 'Failed to load cart.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        const unsubscribe = AuthService.auth.onAuthStateChanged(user => {
            fetchCart();
        });

        fetchCart();
        
        return () => unsubscribe();
    }, [fetchCart]);

    const createPaymentIntent = async () => {
        // --- NEW: Directly use localStorage as the source of truth ---
        const cartUid = localStorage.getItem('cart_uid');
        if (!cartUid) {
            console.error('Active cart not found in localStorage.');
            throw new Error('Active cart not found for this user.');
        }

        try {
            // Use the determined cart UID for the API call.
            const response = await api.post('/api/home/orders/create_payment_intent/', {
                cart_uid: cartUid
            });
            console.log("Payment intent created:", response.data);
            return response.data;
        } catch (err) {
            console.error('Error creating payment intent:', err.response ? err.response.data : err.message);
            const errorMessage = err.response?.data?.cart_uid?.[0] || err.response?.data?.detail || 'Failed to create payment intent.';
            throw new Error(errorMessage);
        }
    };

    const applyCoupon = async (couponCode) => {
        try {
            const response = await api.post('/api/cart/apply_coupon/', { coupon_code: couponCode });
            setCart(response.data);
            return response.data;
        } catch (err) {
            console.error('Error applying coupon:', err.response ? err.response.data : err.message);
            const errorMessage = err.response?.data?.detail || 'Failed to apply coupon.';
            throw new Error(errorMessage);
        }
    };

    const removeCoupon = async () => {
        try {
            const response = await api.post('/api/cart/remove_coupon/');
            setCart(response.data);
            return response.data;
        } catch (err) {
            console.error('Error removing coupon:', err.response ? err.response.data : err.message);
            const errorMessage = err.response?.data?.detail || 'Failed to remove coupon.';
            throw new Error(errorMessage);
        }
    };

    const addToCart = async (productUid, quantity = 1, colorVariantUid = null, sizeVariantUid = null) => {
        try {
            const data = {
                product_uid: productUid,
                quantity: quantity,
                color_variant_uid: colorVariantUid,
                size_variant_uid: sizeVariantUid,
            };
            const response = await api.post('/api/cart/items/', data);
            await fetchCart();
            return response.data;
        } catch (err) {
            console.error('Error adding to cart:', err.response ? err.response.data : err.message);
            const errorMessage = err.response?.data?.non_field_errors?.[0] || err.response?.data?.detail || 'Failed to add item to cart.';
            throw new Error(errorMessage);
        }
    };

    const removeFromCart = async (cartItemUid) => {
        try {
            const response = await api.delete(`/api/cart/items/${cartItemUid}/`);
            await fetchCart();
            return response.data;
        } catch (err) {
            console.error('Error removing from cart:', err.response ? err.response.data : err.message);
            const errorMessage = err.response?.data?.detail || 'Failed to remove item from cart.';
            throw new Error(errorMessage);
        }
    };

    const updateQuantity = async (cartItemUid, quantity) => {
        try {
            const data = { quantity: quantity };
            const response = await api.patch(`/api/cart/items/${cartItemUid}/`, data);
            await fetchCart();
            return response.data;
        } catch (err) {
            console.error('Error updating quantity:', err.response ? err.response.data : err.message);
            const errorMessage = err.response?.data?.quantity?.[0] || err.response?.data?.non_field_errors?.[0] || err.response?.data?.detail || 'Failed to update quantity.';
            throw new Error(errorMessage);
        }
    };

    return (
        <CartContext.Provider value={{
            cart,
            loading,
            error,
            fetchCart,
            addToCart,
            removeFromCart,
            updateQuantity,
            applyCoupon,
            removeCoupon,
            createPaymentIntent,
        }}>
            {children}
        </CartContext.Provider>
    );
};

export const useCart = () => {
    const context = useContext(CartContext);
    if (context === undefined) {
        throw new Error('useCart must be used within a CartProvider');
    }
    return context;
};
