"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CreditCard,
  QrCode,
  Lock,
  AlertCircle,
  CheckCircle,
  Loader2,
  MapPin,
  User,
  Mail,
} from "lucide-react";
import { useRouter } from "next/navigation";
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

interface CheckoutFormProps {
  planId: string;
  planName: string;
  amount: number;
  currency: string;
  billingCycle: "monthly" | "annual";
  onSuccess?: () => void;
  onCancel?: () => void;
}

interface BillingAddress {
  name: string;
  email: string;
  line1: string;
  line2: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
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

// Payment method type
type PaymentMethod = "card" | "qr";

// QR Payment status
type QRPaymentStatus = "pending" | "completed" | "failed" | "expired";

function CheckoutFormContent({
  planId,
  planName,
  amount,
  currency,
  billingCycle,
  onSuccess,
  onCancel,
}: CheckoutFormProps) {
  const router = useRouter();
  const stripe = useStripe();
  const elements = useElements();

  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("card");
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [qrCodeData, setQrCodeData] = useState<string | null>(null);
  const [qrPaymentId, setQrPaymentId] = useState<string | null>(null);
  const [qrPaymentStatus, setQrPaymentStatus] =
    useState<QRPaymentStatus>("pending");
  const [statusCheckInterval, setStatusCheckInterval] =
    useState<NodeJS.Timeout | null>(null);

  const [billingAddress, setBillingAddress] = useState<BillingAddress>({
    name: "",
    email: "",
    line1: "",
    line2: "",
    city: "",
    state: "",
    postal_code: "",
    country: "US",
  });

  // Cleanup status check interval on unmount
  useEffect(() => {
    return () => {
      if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
      }
    };
  }, [statusCheckInterval]);

  // Check QR payment status
  const checkQRPaymentStatus = async (paymentId: string) => {
    try {
      const response = await fetch(
        `/api/payments/qr-code/${paymentId}/status`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to check payment status");
      }

      const data = await response.json();
      const status = data.status as QRPaymentStatus;

      setQrPaymentStatus(status);

      if (status === "completed") {
        // Payment successful
        if (statusCheckInterval) {
          clearInterval(statusCheckInterval);
          setStatusCheckInterval(null);
        }
        toast.success("Payment successful!");
        setTimeout(() => {
          if (onSuccess) {
            onSuccess();
          } else {
            router.push("/dashboard");
          }
        }, 2000);
      } else if (status === "failed" || status === "expired") {
        // Payment failed or expired
        if (statusCheckInterval) {
          clearInterval(statusCheckInterval);
          setStatusCheckInterval(null);
        }
        toast.error(
          status === "failed"
            ? "Payment failed. Please try again."
            : "Payment expired. Please generate a new QR code."
        );
      }
    } catch (error: any) {
      console.error("Error checking payment status:", error);
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!billingAddress.name) {
      newErrors.name = "Name is required";
    }

    if (!billingAddress.email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(billingAddress.email)) {
      newErrors.email = "Email is invalid";
    }

    if (!billingAddress.line1) {
      newErrors.line1 = "Address is required";
    }

    if (!billingAddress.city) {
      newErrors.city = "City is required";
    }

    if (!billingAddress.state) {
      newErrors.state = "State is required";
    }

    if (!billingAddress.postal_code) {
      newErrors.postal_code = "Postal code is required";
    }

    if (!termsAccepted) {
      newErrors.terms = "You must accept the terms and conditions";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle card payment
  const handleCardPayment = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    if (!stripe || !elements) {
      toast.error("Stripe is not loaded");
      return;
    }

    setLoading(true);

    try {
      // Create payment intent
      const intentResponse = await fetch("/api/payments/create-intent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          amount: amount * 100, // Convert to cents
          currency: currency.toLowerCase(),
          plan_id: planId,
          billing_cycle: billingCycle,
        }),
      });

      if (!intentResponse.ok) {
        throw new Error("Failed to create payment intent");
      }

      const intentData = await intentResponse.json();
      const clientSecret = intentData.payment_intent.client_secret;

      // Confirm card payment
      const cardElement = elements.getElement(CardNumberElement);
      if (!cardElement) {
        throw new Error("Card element not found");
      }

      const { error, paymentIntent } = await stripe.confirmCardPayment(
        clientSecret,
        {
          payment_method: {
            card: cardElement,
            billing_details: {
              name: billingAddress.name,
              email: billingAddress.email,
              address: {
                line1: billingAddress.line1,
                line2: billingAddress.line2,
                city: billingAddress.city,
                state: billingAddress.state,
                postal_code: billingAddress.postal_code,
                country: billingAddress.country,
              },
            },
          },
        }
      );

      if (error) {
        throw new Error(error.message);
      }

      if (paymentIntent.status === "succeeded") {
        // Create subscription
        const subscriptionResponse = await fetch("/api/payments/subscribe", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: JSON.stringify({
            plan_id: planId,
            billing_cycle: billingCycle,
            payment_method_id: paymentIntent.payment_method,
          }),
        });

        if (!subscriptionResponse.ok) {
          throw new Error("Failed to create subscription");
        }

        toast.success("Payment successful! Subscription activated.");

        setTimeout(() => {
          if (onSuccess) {
            onSuccess();
          } else {
            router.push("/dashboard");
          }
        }, 2000);
      }
    } catch (error: any) {
      toast.error(error.message || "Payment failed");
      setErrors({ general: error.message });
    } finally {
      setLoading(false);
    }
  };

  // Handle QR code payment
  const handleQRPayment = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Generate QR code
      const response = await fetch("/api/payments/qr-code", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          amount: amount,
          currency: currency,
          plan_id: planId,
          billing_cycle: billingCycle,
          customer_email: billingAddress.email,
          customer_name: billingAddress.name,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate QR code");
      }

      const data = await response.json();

      setQrCodeData(data.qr_code_data);
      setQrPaymentId(data.payment_id);
      setQrPaymentStatus("pending");

      // Start checking payment status every 3 seconds
      const interval = setInterval(() => {
        checkQRPaymentStatus(data.payment_id);
      }, 3000);

      setStatusCheckInterval(interval);

      // Set timeout for 15 minutes
      setTimeout(() => {
        if (statusCheckInterval) {
          clearInterval(statusCheckInterval);
          setStatusCheckInterval(null);
        }
        if (qrPaymentStatus === "pending") {
          setQrPaymentStatus("expired");
          toast.error("Payment expired. Please generate a new QR code.");
        }
      }, 15 * 60 * 1000);

      toast.success("QR code generated! Scan to complete payment.");
    } catch (error: any) {
      toast.error(error.message || "Failed to generate QR code");
      setErrors({ general: error.message });
    } finally {
      setLoading(false);
    }
  };

  // Regenerate QR code
  const regenerateQRCode = () => {
    setQrCodeData(null);
    setQrPaymentId(null);
    setQrPaymentStatus("pending");
    if (statusCheckInterval) {
      clearInterval(statusCheckInterval);
      setStatusCheckInterval(null);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-4xl mx-auto"
    >
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6">
          <h2 className="text-2xl font-bold text-white mb-2">
            Complete Your Purchase
          </h2>
          <p className="text-blue-100">
            Subscribe to {planName} - {currency}{" "}
            {amount.toFixed(2)}/{billingCycle}
          </p>
        </div>

        <div className="p-8">
          {/* Error Message */}
          {errors.general && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-600 dark:text-red-400">
                {errors.general}
              </p>
            </div>
          )}

          {/* Payment Method Tabs */}
          <div className="mb-8">
            <div className="flex gap-4 border-b border-gray-200 dark:border-gray-700">
              <button
                onClick={() => setPaymentMethod("card")}
                className={`flex items-center gap-2 px-6 py-3 font-medium transition-all ${
                  paymentMethod === "card"
                    ? "text-blue-600 dark:text-blue-400 border-b-2 border-blue-600"
                    : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                }`}
              >
                <CreditCard className="w-5 h-5" />
                Credit/Debit Card
              </button>
              <button
                onClick={() => setPaymentMethod("qr")}
                className={`flex items-center gap-2 px-6 py-3 font-medium transition-all ${
                  paymentMethod === "qr"
                    ? "text-blue-600 dark:text-blue-400 border-b-2 border-blue-600"
                    : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                }`}
              >
                <QrCode className="w-5 h-5" />
                UPI/PhonePe QR Code
              </button>
            </div>
          </div>

          {/* Card Payment Form */}
          <AnimatePresence mode="wait">
            {paymentMethod === "card" && !qrCodeData && (
              <motion.form
                key="card-form"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
                onSubmit={handleCardPayment}
                className="space-y-6"
              >
                {/* Billing Information */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Billing Information
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Name */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Full Name
                      </label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="text"
                          value={billingAddress.name}
                          onChange={(e) =>
                            setBillingAddress({
                              ...billingAddress,
                              name: e.target.value,
                            })
                          }
                          className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                            errors.name
                              ? "border-red-500"
                              : "border-gray-300 dark:border-gray-600"
                          } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
                          placeholder="John Doe"
                        />
                      </div>
                      {errors.name && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                          {errors.name}
                        </p>
                      )}
                    </div>

                    {/* Email */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Email Address
                      </label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="email"
                          value={billingAddress.email}
                          onChange={(e) =>
                            setBillingAddress({
                              ...billingAddress,
                              email: e.target.value,
                            })
                          }
                          className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                            errors.email
                              ? "border-red-500"
                              : "border-gray-300 dark:border-gray-600"
                          } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
                          placeholder="john@example.com"
                        />
                      </div>
                      {errors.email && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                          {errors.email}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Address */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Billing Address
                  </h3>
                  <div className="space-y-4">
                    {/* Address Line 1 */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Address Line 1
                      </label>
                      <div className="relative">
                        <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="text"
                          value={billingAddress.line1}
                          onChange={(e) =>
                            setBillingAddress({
                              ...billingAddress,
                              line1: e.target.value,
                            })
                          }
                          className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                            errors.line1
                              ? "border-red-500"
                              : "border-gray-300 dark:border-gray-600"
                          } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
                          placeholder="123 Main St"
                        />
                      </div>
                      {errors.line1 && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                          {errors.line1}
                        </p>
                      )}
                    </div>

                    {/* Address Line 2 */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Address Line 2 (Optional)
                      </label>
                      <input
                        type="text"
                        value={billingAddress.line2}
                        onChange={(e) =>
                          setBillingAddress({
                            ...billingAddress,
                            line2: e.target.value,
                          })
                        }
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        placeholder="Apt, Suite, etc."
                      />
                    </div>

                    {/* City, State, Postal Code */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          City
                        </label>
                        <input
                          type="text"
                          value={billingAddress.city}
                          onChange={(e) =>
                            setBillingAddress({
                              ...billingAddress,
                              city: e.target.value,
                            })
                          }
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                            errors.city
                              ? "border-red-500"
                              : "border-gray-300 dark:border-gray-600"
                          } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
                          placeholder="New York"
                        />
                        {errors.city && (
                          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                            {errors.city}
                          </p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          State
                        </label>
                        <input
                          type="text"
                          value={billingAddress.state}
                          onChange={(e) =>
                            setBillingAddress({
                              ...billingAddress,
                              state: e.target.value,
                            })
                          }
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                            errors.state
                              ? "border-red-500"
                              : "border-gray-300 dark:border-gray-600"
                          } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
                          placeholder="NY"
                        />
                        {errors.state && (
                          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                            {errors.state}
                          </p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Postal Code
                        </label>
                        <input
                          type="text"
                          value={billingAddress.postal_code}
                          onChange={(e) =>
                            setBillingAddress({
                              ...billingAddress,
                              postal_code: e.target.value,
                            })
                          }
                          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                            errors.postal_code
                              ? "border-red-500"
                              : "border-gray-300 dark:border-gray-600"
                          } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
                          placeholder="10001"
                        />
                        {errors.postal_code && (
                          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                            {errors.postal_code}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Card Details */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <Lock className="w-5 h-5 text-green-600" />
                    Secure Card Details
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
                  </div>
                </div>

                {/* Terms and Conditions */}
                <div>
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={termsAccepted}
                      onChange={(e) => setTermsAccepted(e.target.checked)}
                      className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-0.5"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      I agree to the{" "}
                      <a
                        href="/terms"
                        target="_blank"
                        className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
                      >
                        Terms of Service
                      </a>{" "}
                      and{" "}
                      <a
                        href="/privacy"
                        target="_blank"
                        className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
                      >
                        Privacy Policy
                      </a>
                    </span>
                  </label>
                  {errors.terms && (
                    <p className="mt-2 text-sm text-red-600 dark:text-red-400">
                      {errors.terms}
                    </p>
                  )}
                </div>

                {/* Submit Button */}
                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={onCancel}
                    className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
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
                        Processing...
                      </>
                    ) : (
                      <>
                        <Lock className="w-5 h-5" />
                        Pay {currency} {amount.toFixed(2)}
                      </>
                    )}
                  </button>
                </div>
              </motion.form>
            )}

            {/* QR Code Payment Form */}
            {paymentMethod === "qr" && !qrCodeData && (
              <motion.form
                key="qr-form"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
                onSubmit={handleQRPayment}
                className="space-y-6"
              >
                {/* Billing Information */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Contact Information
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Name */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Full Name
                      </label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="text"
                          value={billingAddress.name}
                          onChange={(e) =>
                            setBillingAddress({
                              ...billingAddress,
                              name: e.target.value,
                            })
                          }
                          className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                            errors.name
                              ? "border-red-500"
                              : "border-gray-300 dark:border-gray-600"
                          } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
                          placeholder="John Doe"
                        />
                      </div>
                      {errors.name && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                          {errors.name}
                        </p>
                      )}
                    </div>

                    {/* Email */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Email Address
                      </label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="email"
                          value={billingAddress.email}
                          onChange={(e) =>
                            setBillingAddress({
                              ...billingAddress,
                              email: e.target.value,
                            })
                          }
                          className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                            errors.email
                              ? "border-red-500"
                              : "border-gray-300 dark:border-gray-600"
                          } bg-white dark:bg-gray-700 text-gray-900 dark:text-white`}
                          placeholder="john@example.com"
                        />
                      </div>
                      {errors.email && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                          {errors.email}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Payment Instructions */}
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                    How to pay with UPI/PhonePe:
                  </h4>
                  <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800 dark:text-blue-200">
                    <li>Click "Generate QR Code" below</li>
                    <li>Open your UPI app (PhonePe, Google Pay, Paytm, etc.)</li>
                    <li>Scan the QR code displayed</li>
                    <li>Complete the payment in your app</li>
                    <li>Your subscription will be activated automatically</li>
                  </ol>
                </div>

                {/* Terms and Conditions */}
                <div>
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={termsAccepted}
                      onChange={(e) => setTermsAccepted(e.target.checked)}
                      className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-0.5"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      I agree to the{" "}
                      <a
                        href="/terms"
                        target="_blank"
                        className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
                      >
                        Terms of Service
                      </a>{" "}
                      and{" "}
                      <a
                        href="/privacy"
                        target="_blank"
                        className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
                      >
                        Privacy Policy
                      </a>
                    </span>
                  </label>
                  {errors.terms && (
                    <p className="mt-2 text-sm text-red-600 dark:text-red-400">
                      {errors.terms}
                    </p>
                  )}
                </div>

                {/* Submit Button */}
                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={onCancel}
                    className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <QrCode className="w-5 h-5" />
                        Generate QR Code
                      </>
                    )}
                  </button>
                </div>
              </motion.form>
            )}

            {/* QR Code Display */}
            {qrCodeData && (
              <motion.div
                key="qr-display"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <div className="text-center">
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                    Scan QR Code to Pay
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    Use any UPI app to complete your payment
                  </p>
                </div>

                {/* QR Code */}
                <div className="flex justify-center">
                  <div className="bg-white p-6 rounded-2xl shadow-lg">
                    <img
                      src={qrCodeData}
                      alt="Payment QR Code"
                      className="w-64 h-64"
                    />
                  </div>
                </div>

                {/* Payment Amount */}
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Amount to Pay
                  </p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {currency} {amount.toFixed(2)}
                  </p>
                </div>

                {/* Payment Status */}
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                  <div className="flex items-center justify-center gap-3 mb-4">
                    {qrPaymentStatus === "pending" && (
                      <>
                        <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
                        <span className="text-lg font-semibold text-gray-900 dark:text-white">
                          Waiting for payment...
                        </span>
                      </>
                    )}
                    {qrPaymentStatus === "completed" && (
                      <>
                        <CheckCircle className="w-6 h-6 text-green-600" />
                        <span className="text-lg font-semibold text-green-600">
                          Payment Successful!
                        </span>
                      </>
                    )}
                    {qrPaymentStatus === "failed" && (
                      <>
                        <AlertCircle className="w-6 h-6 text-red-600" />
                        <span className="text-lg font-semibold text-red-600">
                          Payment Failed
                        </span>
                      </>
                    )}
                    {qrPaymentStatus === "expired" && (
                      <>
                        <AlertCircle className="w-6 h-6 text-orange-600" />
                        <span className="text-lg font-semibold text-orange-600">
                          QR Code Expired
                        </span>
                      </>
                    )}
                  </div>

                  {qrPaymentStatus === "pending" && (
                    <p className="text-sm text-center text-gray-600 dark:text-gray-400">
                      Checking payment status every 3 seconds...
                      <br />
                      This QR code will expire in 15 minutes.
                    </p>
                  )}

                  {(qrPaymentStatus === "failed" ||
                    qrPaymentStatus === "expired") && (
                    <div className="text-center">
                      <button
                        onClick={regenerateQRCode}
                        className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                      >
                        Generate New QR Code
                      </button>
                    </div>
                  )}
                </div>

                {/* Instructions */}
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                    Payment Instructions:
                  </h4>
                  <ul className="space-y-1 text-sm text-blue-800 dark:text-blue-200">
                    <li>• Open your UPI app (PhonePe, Google Pay, Paytm, etc.)</li>
                    <li>• Tap on "Scan QR Code"</li>
                    <li>• Point your camera at the QR code above</li>
                    <li>• Verify the amount and complete the payment</li>
                    <li>• Your subscription will be activated automatically</li>
                  </ul>
                </div>

                {/* Cancel Button */}
                {qrPaymentStatus === "pending" && (
                  <div className="text-center">
                    <button
                      onClick={() => {
                        if (statusCheckInterval) {
                          clearInterval(statusCheckInterval);
                          setStatusCheckInterval(null);
                        }
                        regenerateQRCode();
                        if (onCancel) {
                          onCancel();
                        }
                      }}
                      className="px-6 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 font-medium"
                    >
                      Cancel Payment
                    </button>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Security Badge */}
          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <Lock className="w-4 h-4" />
              <span>
                Secured by Stripe and PhonePe. Your payment information is
                encrypted and secure.
              </span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Main component with Stripe Elements wrapper
export default function CheckoutForm(props: CheckoutFormProps) {
  return (
    <Elements stripe={stripePromise}>
      <CheckoutFormContent {...props} />
    </Elements>
  );
}
