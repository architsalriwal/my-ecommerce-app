// C:\Users\archi\Downloads\Folder2\frontend\src\components\StripePaymentForm.jsx

import React, { useState } from 'react';
import { useStripe, useElements, PaymentElement } from '@stripe/react-stripe-js'; 
import { Button, CircularProgress, Alert } from '@mui/material'; 

const StripePaymentForm = ({ orderData, onPaymentSuccess, onPaymentFailure }) => {
    const stripe = useStripe();
    const elements = useElements(); 
    const [message, setMessage] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault();

        if (!stripe || !elements) {
            setMessage("Stripe.js has not yet loaded or Elements are not initialized. Please try again.");
            return;
        }

        setIsLoading(true);
        setMessage(null); 

        try {
            const { error: stripeError, paymentIntent } = await stripe.confirmPayment({
                elements,
                confirmParams: {
                    return_url: `${window.location.origin}/order-success/${orderData.order_uid}`, 
                },
                redirect: 'if_required' 
            });

            if (stripeError) {
                setIsLoading(false);
                if (stripeError.type === "card_error" || stripeError.type === "validation_error") {
                    setMessage(stripeError.message);
                } else {
                    setMessage("An unexpected error occurred during payment confirmation.");
                }
                console.error("Stripe confirmPayment error:", stripeError);
                if (onPaymentFailure) onPaymentFailure(stripeError);
            } else if (paymentIntent && paymentIntent.status === 'succeeded') {
                onPaymentSuccess(orderData.order_uid); 
            } else if (paymentIntent && paymentIntent.status === 'requires_action') {
                console.log("Payment requires action, Stripe will redirect.");
            }
        } catch (error) {
            setIsLoading(false);
            setMessage(`An unexpected error occurred: ${error.message}`);
            console.error("Stripe confirmPayment unexpected error:", error);
            if (onPaymentFailure) onPaymentFailure(error);
        }
    };

    return (
        <form id="stripe-payment-form" onSubmit={handleSubmit}>
            <PaymentElement id="payment-element" />
            
            {message && (
                <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
                    {message}
                </Alert>
            )}

            <Button
                type="submit"
                fullWidth
                variant="contained"
                color="primary"
                disabled={isLoading || !stripe || !elements} 
                sx={{ mt: 3 }}
            >
                {isLoading ? <CircularProgress size={24} color="inherit" /> : "Pay Now"}
            </Button>
        </form>
    );
};

export default StripePaymentForm;