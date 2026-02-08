"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CreditCard,
  Plus,
  Trash2,
  Edit,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";
import toast from "react-hot-toast";
import { loadStripe } from "@stripe/stripe-js";
import {
  Elements,
  CardNumberElement,
  CardExpiryElement,
  CardCvcElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";

// Initialize Stripe
const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || ""
);

interface PaymentMethodData {
  payment_method_id: string;
  type: string;
  card_brand?: string;
  card_last4?: string;
  card_exp_month?: number;
  card_exp_year?: number;
  is_default: boolean;
}

interface PaymentMethodProps {
  onUpdate?: () => void;
}

// Stripe card element styles
const cardElementOptions = {
  style: {
    base: {
      fontSize: "16px",
      color: "#1f2937",
      "::placeholder": {
        color: "#9ca3af",
      },
    },
    invalid: {
      color: "#ef4444",
    },
  },
};

function AddPaymentMethodForm({ onSuccess, onCancel }: { onSuccess: () => void; onCancel: () => void }) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [setAsDefault, setSetAsDefault] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      toast.error("Stripe is not loaded");
      return;
    }

    setLoading(true);

    try {
      const cardElement = elements.getElement(CardNumberElement);
      if (!cardElement) {
        throw new Error("Card element not found");
      }

      // Create payment method
      const { error, paymentMethod } = await stripe.createPaymentMethod({
        type: "card",
        card: cardElement,
      });

      if (error) {
        throw new Error(error.message);
      }

      // Add payment method to backend
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/payments/update-payment-method", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          payment_method_id: paymentMethod.id,
          set_as_default: setAsDefault,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to add payment method");
      }

      toast.success("Payment method added successfully");
      onSuccess();
    } catch (error: any) {
      toast.error(error.message || "Failed to add payment method");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Add New Payment Method
        </h3>

        <div className="space-y-4">
          {/* Card Number */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Card Number
            </label>
            <div className="p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
              <CardNumberElement options={cardElementOptions} />
            </div>
          </div>

          {/* Expiry and CVC */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Expiry Date
              </label>
              <div className="p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
                <CardExpiryElement options={cardElementOptions} />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                CVC
              </label>
              <div className="p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
                <CardCvcElement options={cardElementOptions} />
              </div>
            </div>
          </div>

          {/* Set as Default */}
          <div>
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={setAsDefault}
                onChange={(e) => setSetAsDefault(e.target.checked)}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Set as default payment method
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Buttons */}
      <div className="flex gap-4">
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading || !stripe}
          className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Adding...
            </>
          ) : (
            <>
              <Plus className="w-5 h-5" />
              Add Payment Method
            </>
          )}
        </button>
      </div>
    </form>
  );
}

export default function PaymentMethod({ onUpdate }: PaymentMethodProps) {
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethodData[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [deletingMethod, setDeletingMethod] = useState<string | null>(null);
  const [updatingDefault, setUpdatingDefault] = useState<string | null>(null);

  useEffect(() => {
    fetchPaymentMethods();
  }, []);

  const fetchPaymentMethods = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/payments/subscription", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch payment methods");
      }

      const data = await response.json();
      // Assuming the API returns payment methods in the subscription data
      setPaymentMethods(data.payment_methods || []);
    } catch (error: any) {
      toast.error("Failed to load payment methods");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemovePaymentMethod = async (paymentMethodId: string) => {
    if (!confirm("Are you sure you want to remove this payment method?")) {
      return;
    }

    setDeletingMethod(paymentMethodId);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/payments/update-payment-method", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          payment_method_id: paymentMethodId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to remove payment method");
      }

      toast.success("Payment method removed successfully");
      await fetchPaymentMethods();

      if (onUpdate) {
        onUpdate();
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to remove payment method");
    } finally {
      setDeletingMethod(null);
    }
  };

  const handleSetDefaultPaymentMethod = async (paymentMethodId: string) => {
    setUpdatingDefault(paymentMethodId);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/payments/update-payment-method", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          payment_method_id: paymentMethodId,
          set_as_default: true,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to update default payment method");
      }

      toast.success("Default payment method updated");
      await fetchPaymentMethods();

      if (onUpdate) {
        onUpdate();
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to update default payment method");
    } finally {
      setUpdatingDefault(null);
    }
  };

  const handleAddSuccess = async () => {
    setShowAddForm(false);
    await fetchPaymentMethods();

    if (onUpdate) {
      onUpdate();
    }
  };

  const getCardBrandIcon = (brand: string) => {
    // You can add specific card brand icons here
    return <CreditCard className="w-6 h-6" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-600 dark:text-gray-400">
            Loading payment methods...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Payment Methods
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Manage your payment methods for subscriptions
        </p>
      </div>

      {/* Payment Methods List */}
      <div className="space-y-4 mb-6">
        {paymentMethods.length === 0 && !showAddForm ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 text-center"
          >
            <CreditCard className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              No Payment Methods
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Add a payment method to manage your subscriptions
            </p>
            <button
              onClick={() => setShowAddForm(true)}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center gap-2 mx-auto"
            >
              <Plus className="w-5 h-5" />
              Add Payment Method
            </button>
          </motion.div>
        ) : (
          <>
            {paymentMethods.map((method, index) => (
              <motion.div
                key={method.payment_method_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center text-blue-600 dark:text-blue-400">
                      {getCardBrandIcon(method.card_brand || "card")}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                          {method.card_brand || "Card"} •••• {method.card_last4}
                        </h3>
                        {method.is_default && (
                          <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 text-xs font-semibold rounded-full flex items-center gap-1">
                            <CheckCircle className="w-3 h-3" />
                            Default
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Expires {method.card_exp_month}/{method.card_exp_year}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {!method.is_default && (
                      <button
                        onClick={() => handleSetDefaultPaymentMethod(method.payment_method_id)}
                        disabled={updatingDefault === method.payment_method_id}
                        className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2 disabled:opacity-50"
                      >
                        {updatingDefault === method.payment_method_id ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Setting...
                          </>
                        ) : (
                          <>
                            <Edit className="w-4 h-4" />
                            Set as Default
                          </>
                        )}
                      </button>
                    )}
                    <button
                      onClick={() => handleRemovePaymentMethod(method.payment_method_id)}
                      disabled={deletingMethod === method.payment_method_id || method.is_default}
                      className="px-4 py-2 border border-red-300 dark:border-red-700 rounded-lg text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      title={method.is_default ? "Cannot remove default payment method" : "Remove payment method"}
                    >
                      {deletingMethod === method.payment_method_id ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Removing...
                        </>
                      ) : (
                        <>
                          <Trash2 className="w-4 h-4" />
                          Remove
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}

            {/* Add New Button */}
            {!showAddForm && (
              <motion.button
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: paymentMethods.length * 0.1 }}
                onClick={() => setShowAddForm(true)}
                className="w-full bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-blue-600 dark:hover:border-blue-400 transition-colors flex items-center justify-center gap-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 font-semibold"
              >
                <Plus className="w-5 h-5" />
                Add New Payment Method
              </motion.button>
            )}
          </>
        )}
      </div>

      {/* Add Payment Method Form */}
      <AnimatePresence>
        {showAddForm && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6"
          >
            <Elements stripe={stripePromise}>
              <AddPaymentMethodForm
                onSuccess={handleAddSuccess}
                onCancel={() => setShowAddForm(false)}
              />
            </Elements>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Info Message */}
      {paymentMethods.length > 0 && (
        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-600 dark:text-blue-400">
            <p className="font-semibold mb-1">Payment Method Information</p>
            <p>
              Your default payment method will be used for all subscription renewals.
              You cannot remove your default payment method while you have an active subscription.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
