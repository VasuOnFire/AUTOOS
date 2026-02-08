"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  QrCode,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  Smartphone,
  AlertCircle,
  Loader2,
  Copy,
  ExternalLink,
} from "lucide-react";
import toast from "react-hot-toast";
import QRCodeLib from "qrcode";

interface QRCodePaymentProps {
  amount: number;
  currency: string;
  planId: string;
  billingCycle: "monthly" | "annual";
  customerEmail: string;
  customerName: string;
  onSuccess?: () => void;
  onCancel?: () => void;
  onExpire?: () => void;
}

type PaymentStatus = "pending" | "completed" | "failed" | "expired";

export default function QRCodePayment({
  amount,
  currency,
  planId,
  billingCycle,
  customerEmail,
  customerName,
  onSuccess,
  onCancel,
  onExpire,
}: QRCodePaymentProps) {
  const [qrCodeData, setQrCodeData] = useState<string | null>(null);
  const [qrCodeImage, setQrCodeImage] = useState<string | null>(null);
  const [paymentId, setPaymentId] = useState<string | null>(null);
  const [paymentStatus, setPaymentStatus] = useState<PaymentStatus>("pending");
  const [loading, setLoading] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(15 * 60); // 15 minutes in seconds
  const [upiId, setUpiId] = useState<string>("");
  
  const statusCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const timerIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    generateQRCode();

    return () => {
      // Cleanup intervals on unmount
      if (statusCheckIntervalRef.current) {
        clearInterval(statusCheckIntervalRef.current);
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
    };
  }, []);

  const generateQRCode = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/payments/qr-code", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          amount,
          currency,
          plan_id: planId,
          billing_cycle: billingCycle,
          customer_email: customerEmail,
          customer_name: customerName,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate QR code");
      }

      const data = await response.json();

      setQrCodeData(data.qr_code_data);
      setPaymentId(data.payment_id);
      setUpiId(data.upi_id || "");
      setPaymentStatus("pending");
      setTimeRemaining(15 * 60);

      // Generate QR code image
      const qrImage = await QRCodeLib.toDataURL(data.qr_code_data, {
        width: 300,
        margin: 2,
        color: {
          dark: "#000000",
          light: "#FFFFFF",
        },
      });
      setQrCodeImage(qrImage);

      // Start checking payment status every 3 seconds
      const interval = setInterval(() => {
        checkPaymentStatus(data.payment_id);
      }, 3000);
      statusCheckIntervalRef.current = interval;

      // Start countdown timer
      const timerInterval = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            clearInterval(timerInterval);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      timerIntervalRef.current = timerInterval;

      // Set timeout for 15 minutes
      const timeout = setTimeout(() => {
        if (statusCheckIntervalRef.current) {
          clearInterval(statusCheckIntervalRef.current);
        }
        if (timerIntervalRef.current) {
          clearInterval(timerIntervalRef.current);
        }
        if (paymentStatus === "pending") {
          setPaymentStatus("expired");
          toast.error("Payment expired. Please generate a new QR code.");
          if (onExpire) {
            onExpire();
          }
        }
      }, 15 * 60 * 1000);
      timeoutRef.current = timeout;

      toast.success("QR code generated! Scan to complete payment.");
    } catch (error: any) {
      toast.error(error.message || "Failed to generate QR code");
      setPaymentStatus("failed");
    } finally {
      setLoading(false);
    }
  };

  const checkPaymentStatus = async (paymentIdToCheck: string) => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `/api/payments/qr-code/${paymentIdToCheck}/status`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        return;
      }

      const data = await response.json();
      const status = data.status as PaymentStatus;

      setPaymentStatus(status);

      if (status === "completed") {
        // Payment successful
        if (statusCheckIntervalRef.current) {
          clearInterval(statusCheckIntervalRef.current);
        }
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
        if (timerIntervalRef.current) {
          clearInterval(timerIntervalRef.current);
        }
        toast.success("Payment successful!");
        setTimeout(() => {
          if (onSuccess) {
            onSuccess();
          }
        }, 2000);
      } else if (status === "failed" || status === "expired") {
        // Payment failed or expired
        if (statusCheckIntervalRef.current) {
          clearInterval(statusCheckIntervalRef.current);
        }
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
        if (timerIntervalRef.current) {
          clearInterval(timerIntervalRef.current);
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

  const handleRegenerateQRCode = () => {
    // Clear existing intervals
    if (statusCheckIntervalRef.current) {
      clearInterval(statusCheckIntervalRef.current);
    }
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
    }

    // Reset state
    setQrCodeData(null);
    setQrCodeImage(null);
    setPaymentId(null);
    setPaymentStatus("pending");

    // Generate new QR code
    generateQRCode();
  };

  const handleCopyUpiId = () => {
    if (upiId) {
      navigator.clipboard.writeText(upiId);
      toast.success("UPI ID copied to clipboard");
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, "0")}`;
  };

  const getStatusIcon = () => {
    switch (paymentStatus) {
      case "completed":
        return <CheckCircle className="w-16 h-16 text-green-600 dark:text-green-400" />;
      case "failed":
        return <XCircle className="w-16 h-16 text-red-600 dark:text-red-400" />;
      case "expired":
        return <Clock className="w-16 h-16 text-orange-600 dark:text-orange-400" />;
      default:
        return <Loader2 className="w-16 h-16 text-blue-600 dark:text-blue-400 animate-spin" />;
    }
  };

  const getStatusMessage = () => {
    switch (paymentStatus) {
      case "completed":
        return "Payment Successful!";
      case "failed":
        return "Payment Failed";
      case "expired":
        return "Payment Expired";
      default:
        return "Waiting for Payment...";
    }
  };

  if (loading && !qrCodeImage) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
          <p className="text-gray-600 dark:text-gray-400">
            Generating QR code...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">
                UPI/PhonePe Payment
              </h2>
              <p className="text-purple-100">
                Scan QR code to pay {currency} {amount.toFixed(2)}
              </p>
            </div>
            <QrCode className="w-12 h-12 text-white" />
          </div>
        </div>

        <div className="p-8">
          {/* Payment Status */}
          <AnimatePresence mode="wait">
            {paymentStatus !== "pending" ? (
              <motion.div
                key="status"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="text-center py-8"
              >
                <div className="flex justify-center mb-4">
                  {getStatusIcon()}
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {getStatusMessage()}
                </h3>
                {paymentStatus === "completed" && (
                  <p className="text-gray-600 dark:text-gray-400 mb-6">
                    Your subscription has been activated successfully.
                  </p>
                )}
                {(paymentStatus === "failed" || paymentStatus === "expired") && (
                  <div className="space-y-4">
                    <p className="text-gray-600 dark:text-gray-400">
                      {paymentStatus === "failed"
                        ? "The payment could not be processed. Please try again."
                        : "The QR code has expired. Please generate a new one."}
                    </p>
                    <div className="flex gap-4 justify-center">
                      <button
                        onClick={handleRegenerateQRCode}
                        className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all duration-200 flex items-center gap-2"
                      >
                        <RefreshCw className="w-5 h-5" />
                        Generate New QR Code
                      </button>
                      {onCancel && (
                        <button
                          onClick={onCancel}
                          className="px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </motion.div>
            ) : (
              <motion.div
                key="qr-code"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-6"
              >
                {/* Timer */}
                <div className="flex items-center justify-center gap-2 text-orange-600 dark:text-orange-400">
                  <Clock className="w-5 h-5" />
                  <span className="text-lg font-semibold">
                    Time Remaining: {formatTime(timeRemaining)}
                  </span>
                </div>

                {/* QR Code */}
                <div className="flex justify-center">
                  <div className="bg-white p-6 rounded-2xl shadow-lg">
                    {qrCodeImage && (
                      <img
                        src={qrCodeImage}
                        alt="Payment QR Code"
                        className="w-64 h-64"
                      />
                    )}
                  </div>
                </div>

                {/* Instructions */}
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4 flex items-center gap-2">
                    <Smartphone className="w-5 h-5" />
                    How to Pay
                  </h3>
                  <ol className="space-y-3 text-blue-800 dark:text-blue-200">
                    <li className="flex items-start gap-3">
                      <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                        1
                      </span>
                      <span>Open PhonePe, Google Pay, Paytm, or any UPI app</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                        2
                      </span>
                      <span>Scan the QR code above</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                        3
                      </span>
                      <span>Verify the amount and complete the payment</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                        4
                      </span>
                      <span>Wait for confirmation (this page will update automatically)</span>
                    </li>
                  </ol>
                </div>

                {/* UPI ID */}
                {upiId && (
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      Or pay directly using UPI ID:
                    </p>
                    <div className="flex items-center gap-2">
                      <code className="flex-1 bg-white dark:bg-gray-800 px-4 py-2 rounded-lg text-gray-900 dark:text-white font-mono text-sm">
                        {upiId}
                      </code>
                      <button
                        onClick={handleCopyUpiId}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                      >
                        <Copy className="w-4 h-4" />
                        Copy
                      </button>
                    </div>
                  </div>
                )}

                {/* Payment Details */}
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                    Payment Details
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Amount:</span>
                      <span className="font-semibold text-gray-900 dark:text-white">
                        {currency} {amount.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Merchant:</span>
                      <span className="font-semibold text-gray-900 dark:text-white">
                        AUTOOS
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Payment ID:</span>
                      <span className="font-mono text-xs text-gray-900 dark:text-white">
                        {paymentId}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Status Indicator */}
                <div className="flex items-center justify-center gap-3 text-blue-600 dark:text-blue-400">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span className="text-sm font-medium">
                    Checking payment status every 3 seconds...
                  </span>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-4">
                  <button
                    onClick={handleRegenerateQRCode}
                    disabled={loading}
                    className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    <RefreshCw className="w-5 h-5" />
                    Regenerate QR Code
                  </button>
                  {onCancel && (
                    <button
                      onClick={onCancel}
                      disabled={loading}
                      className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Support Info */}
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-gray-600 dark:text-gray-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-gray-600 dark:text-gray-400">
              <p className="font-semibold mb-1">Need Help?</p>
              <p>
                If you're having trouble with the payment, please contact our support team.
                The QR code will expire in 15 minutes for security reasons.
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
