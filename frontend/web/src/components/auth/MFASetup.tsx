"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Shield,
  Download,
  Copy,
  Check,
  AlertCircle,
  Smartphone,
  Key,
} from "lucide-react";
import toast from "react-hot-toast";
import QRCode from "qrcode";

interface MFASetupProps {
  onComplete?: () => void;
  onCancel?: () => void;
}

export default function MFASetup({ onComplete, onCancel }: MFASetupProps) {
  const [step, setStep] = useState<"setup" | "verify">("setup");
  const [qrCodeUrl, setQrCodeUrl] = useState("");
  const [secretKey, setSecretKey] = useState("");
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [verificationCode, setVerificationCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copiedSecret, setCopiedSecret] = useState(false);
  const [copiedBackupCodes, setCopiedBackupCodes] = useState(false);

  useEffect(() => {
    setupMFA();
  }, []);

  const setupMFA = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/auth/mfa/setup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to setup MFA");
      }

      setSecretKey(data.secret);
      setBackupCodes(data.backup_codes);

      // Generate QR code
      const qrUrl = await QRCode.toDataURL(data.qr_uri);
      setQrCodeUrl(qrUrl);
    } catch (error: any) {
      toast.error(error.message || "Failed to setup MFA");
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopySecret = () => {
    navigator.clipboard.writeText(secretKey);
    setCopiedSecret(true);
    toast.success("Secret key copied!");
    setTimeout(() => setCopiedSecret(false), 2000);
  };

  const handleCopyBackupCodes = () => {
    navigator.clipboard.writeText(backupCodes.join("\n"));
    setCopiedBackupCodes(true);
    toast.success("Backup codes copied!");
    setTimeout(() => setCopiedBackupCodes(false), 2000);
  };

  const handleDownloadBackupCodes = () => {
    const blob = new Blob([backupCodes.join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "autoos-backup-codes.txt";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success("Backup codes downloaded!");
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();

    if (verificationCode.length !== 6) {
      setError("Please enter a 6-digit code");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch("/api/auth/mfa/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          code: verificationCode,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Verification failed");
      }

      toast.success("MFA enabled successfully!");
      if (onComplete) {
        onComplete();
      }
    } catch (error: any) {
      toast.error(error.message || "Verification failed");
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !qrCodeUrl) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-2xl mx-auto"
    >
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
            <Shield className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {step === "setup" ? "Set Up Two-Factor Authentication" : "Verify Your Setup"}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {step === "setup"
              ? "Add an extra layer of security to your account"
              : "Enter the code from your authenticator app"}
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {step === "setup" ? (
          <div className="space-y-8">
            {/* Step 1: Scan QR Code */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  1
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Scan QR Code
                </h3>
              </div>
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 flex flex-col items-center">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 text-center">
                  Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
                </p>
                {qrCodeUrl && (
                  <img
                    src={qrCodeUrl}
                    alt="MFA QR Code"
                    className="w-48 h-48 border-4 border-white dark:border-gray-800 rounded-lg"
                  />
                )}
                <div className="mt-4 flex items-center gap-2">
                  <Smartphone className="w-5 h-5 text-gray-400" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Use your phone's camera
                  </span>
                </div>
              </div>
            </div>

            {/* Step 2: Manual Entry */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  2
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Or Enter Manually
                </h3>
              </div>
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  If you can't scan the QR code, enter this secret key manually:
                </p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-3 font-mono text-sm">
                    {secretKey}
                  </div>
                  <button
                    onClick={handleCopySecret}
                    className="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                  >
                    {copiedSecret ? (
                      <Check className="w-5 h-5" />
                    ) : (
                      <Copy className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Step 3: Backup Codes */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  3
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Save Backup Codes
                </h3>
              </div>
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
                <div className="flex items-start gap-3 mb-4">
                  <Key className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-yellow-800 dark:text-yellow-300 mb-1">
                      Important: Save these backup codes
                    </p>
                    <p className="text-sm text-yellow-700 dark:text-yellow-400">
                      Use these codes to access your account if you lose your device. Each code can only be used once.
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 mb-4">
                  {backupCodes.map((code, index) => (
                    <div
                      key={index}
                      className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded px-3 py-2 font-mono text-sm text-center"
                    >
                      {code}
                    </div>
                  ))}
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={handleDownloadBackupCodes}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    <span className="text-sm font-medium">Download</span>
                  </button>
                  <button
                    onClick={handleCopyBackupCodes}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    {copiedBackupCodes ? (
                      <Check className="w-4 h-4" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                    <span className="text-sm font-medium">
                      {copiedBackupCodes ? "Copied!" : "Copy"}
                    </span>
                  </button>
                </div>
              </div>
            </div>

            {/* Continue Button */}
            <div className="flex gap-4">
              {onCancel && (
                <button
                  onClick={onCancel}
                  className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
              )}
              <button
                onClick={() => setStep("verify")}
                className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
              >
                Continue to Verification
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleVerify} className="space-y-6">
            <div>
              <label
                htmlFor="verificationCode"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Enter 6-Digit Code
              </label>
              <input
                id="verificationCode"
                type="text"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ""))}
                maxLength={6}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-center text-2xl font-mono tracking-widest"
                placeholder="000000"
                autoFocus
              />
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Open your authenticator app and enter the 6-digit code
              </p>
            </div>

            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setStep("setup")}
                className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Back
              </button>
              <button
                type="submit"
                disabled={loading || verificationCode.length !== 6}
                className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Verifying...
                  </div>
                ) : (
                  "Enable MFA"
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </motion.div>
  );
}
