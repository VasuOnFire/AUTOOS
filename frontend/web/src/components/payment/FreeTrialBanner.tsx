"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Clock,
  Zap,
  ArrowRight,
  X,
  TrendingUp,
  Gift,
  Star,
} from "lucide-react";
import toast from "react-hot-toast";

interface TrialStatus {
  is_active: boolean;
  trial_start_date: string;
  trial_end_date: string;
  days_remaining: number;
  credits_remaining: number;
  initial_credits: number;
}

interface FreeTrialBannerProps {
  onUpgrade?: () => void;
  onDismiss?: () => void;
  dismissible?: boolean;
}

export default function FreeTrialBanner({
  onUpgrade,
  onDismiss,
  dismissible = false,
}: FreeTrialBannerProps) {
  const [trialStatus, setTrialStatus] = useState<TrialStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [dismissed, setDismissed] = useState(false);
  const [timeLeft, setTimeLeft] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  });

  useEffect(() => {
    fetchTrialStatus();
  }, []);

  useEffect(() => {
    if (trialStatus && trialStatus.is_active) {
      // Update countdown every second
      const interval = setInterval(() => {
        updateCountdown();
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [trialStatus]);

  const fetchTrialStatus = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/payments/trial-status", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch trial status");
      }

      const data = await response.json();
      setTrialStatus(data);
      updateCountdown(data);
    } catch (error: any) {
      console.error("Failed to load trial status:", error);
    } finally {
      setLoading(false);
    }
  };

  const updateCountdown = (status?: TrialStatus) => {
    const trial = status || trialStatus;
    if (!trial || !trial.is_active) return;

    const endDate = new Date(trial.trial_end_date);
    const now = new Date();
    const diff = endDate.getTime() - now.getTime();

    if (diff <= 0) {
      setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 });
      return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    setTimeLeft({ days, hours, minutes, seconds });
  };

  const handleDismiss = () => {
    setDismissed(true);
    if (onDismiss) {
      onDismiss();
    }
  };

  const handleUpgrade = () => {
    if (onUpgrade) {
      onUpgrade();
    }
  };

  const getCreditsPercentage = () => {
    if (!trialStatus) return 0;
    return (trialStatus.credits_remaining / trialStatus.initial_credits) * 100;
  };

  const getUrgencyLevel = () => {
    if (!trialStatus) return "normal";
    if (trialStatus.days_remaining <= 3) return "critical";
    if (trialStatus.days_remaining <= 7) return "warning";
    return "normal";
  };

  const getCreditsUrgency = () => {
    const percentage = getCreditsPercentage();
    if (percentage <= 20) return "critical";
    if (percentage <= 50) return "warning";
    return "normal";
  };

  if (loading || !trialStatus || !trialStatus.is_active || dismissed) {
    return null;
  }

  const urgencyLevel = getUrgencyLevel();
  const creditsUrgency = getCreditsUrgency();

  // Determine banner color based on urgency
  const getBannerGradient = () => {
    if (urgencyLevel === "critical") {
      return "from-red-600 to-orange-600";
    }
    if (urgencyLevel === "warning") {
      return "from-orange-600 to-yellow-600";
    }
    return "from-green-600 to-emerald-600";
  };

  const getProgressBarColor = () => {
    if (creditsUrgency === "critical") return "bg-red-600";
    if (creditsUrgency === "warning") return "bg-yellow-600";
    return "bg-green-600";
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.5 }}
        className="relative"
      >
        <div
          className={`bg-gradient-to-r ${getBannerGradient()} rounded-2xl shadow-2xl overflow-hidden`}
        >
          {/* Dismiss Button */}
          {dismissible && (
            <button
              onClick={handleDismiss}
              className="absolute top-4 right-4 p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors z-10"
            >
              <X className="w-5 h-5 text-white" />
            </button>
          )}

          <div className="p-6 md:p-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main Message */}
              <div className="lg:col-span-2">
                <div className="flex items-start gap-4 mb-6">
                  <div className="w-14 h-14 bg-white/20 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl md:text-3xl font-bold text-white mb-2">
                      {urgencyLevel === "critical"
                        ? "⚠️ Trial Ending Soon!"
                        : urgencyLevel === "warning"
                        ? "Your Free Trial is Active"
                        : "🎉 Enjoying Your Free Trial?"}
                    </h2>
                    <p className="text-white/90 text-lg">
                      {urgencyLevel === "critical"
                        ? "Your trial expires in less than 3 days. Upgrade now to keep your workflows running!"
                        : urgencyLevel === "warning"
                        ? "Don't miss out! Upgrade before your trial ends to continue using all features."
                        : "Experience the full power of AUTOOS with no credit card required!"}
                    </p>
                  </div>
                </div>

                {/* Trial Benefits */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Gift className="w-5 h-5 text-white" />
                      <span className="text-white/80 text-sm font-medium">
                        Trial Benefits
                      </span>
                    </div>
                    <p className="text-2xl font-bold text-white">
                      30 Days Free
                    </p>
                    <p className="text-white/70 text-sm">No credit card needed</p>
                  </div>

                  <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Zap className="w-5 h-5 text-white" />
                      <span className="text-white/80 text-sm font-medium">
                        Workflows
                      </span>
                    </div>
                    <p className="text-2xl font-bold text-white">
                      10 / month
                    </p>
                    <p className="text-white/70 text-sm">Included in trial</p>
                  </div>

                  <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Star className="w-5 h-5 text-white" />
                      <span className="text-white/80 text-sm font-medium">
                        Agents
                      </span>
                    </div>
                    <p className="text-2xl font-bold text-white">
                      2 Concurrent
                    </p>
                    <p className="text-white/70 text-sm">Full access</p>
                  </div>
                </div>

                {/* Upgrade Button */}
                <button
                  onClick={handleUpgrade}
                  className="bg-white text-gray-900 px-8 py-4 rounded-xl font-bold text-lg hover:bg-gray-100 transition-all duration-200 flex items-center gap-3 shadow-xl hover:shadow-2xl transform hover:scale-105"
                >
                  <TrendingUp className="w-6 h-6" />
                  Upgrade Now & Save 17%
                  <ArrowRight className="w-6 h-6" />
                </button>
              </div>

              {/* Countdown & Stats */}
              <div className="space-y-4">
                {/* Countdown Timer */}
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Clock className="w-5 h-5 text-white" />
                    <span className="text-white font-semibold">Time Remaining</span>
                  </div>

                  <div className="grid grid-cols-4 gap-2 mb-4">
                    <div className="text-center">
                      <div className="bg-white/20 rounded-lg p-3 mb-1">
                        <span className="text-3xl font-bold text-white">
                          {timeLeft.days}
                        </span>
                      </div>
                      <span className="text-white/70 text-xs">Days</span>
                    </div>
                    <div className="text-center">
                      <div className="bg-white/20 rounded-lg p-3 mb-1">
                        <span className="text-3xl font-bold text-white">
                          {timeLeft.hours}
                        </span>
                      </div>
                      <span className="text-white/70 text-xs">Hours</span>
                    </div>
                    <div className="text-center">
                      <div className="bg-white/20 rounded-lg p-3 mb-1">
                        <span className="text-3xl font-bold text-white">
                          {timeLeft.minutes}
                        </span>
                      </div>
                      <span className="text-white/70 text-xs">Mins</span>
                    </div>
                    <div className="text-center">
                      <div className="bg-white/20 rounded-lg p-3 mb-1">
                        <span className="text-3xl font-bold text-white">
                          {timeLeft.seconds}
                        </span>
                      </div>
                      <span className="text-white/70 text-xs">Secs</span>
                    </div>
                  </div>

                  <p className="text-white/80 text-sm text-center">
                    Trial expires on{" "}
                    {new Date(trialStatus.trial_end_date).toLocaleDateString("en-US", {
                      month: "long",
                      day: "numeric",
                      year: "numeric",
                    })}
                  </p>
                </div>

                {/* Credits Remaining */}
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Zap className="w-5 h-5 text-white" />
                      <span className="text-white font-semibold">Credits</span>
                    </div>
                    <span className="text-white font-bold text-lg">
                      {trialStatus.credits_remaining} / {trialStatus.initial_credits}
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-white/20 rounded-full h-3 mb-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${getCreditsPercentage()}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                      className={`h-3 rounded-full ${getProgressBarColor()}`}
                    />
                  </div>

                  <p className="text-white/70 text-sm">
                    {creditsUrgency === "critical"
                      ? "⚠️ Running low on credits!"
                      : creditsUrgency === "warning"
                      ? "Consider upgrading for unlimited workflows"
                      : "Plenty of credits remaining"}
                  </p>
                </div>

                {/* Upgrade Reminder */}
                {urgencyLevel !== "normal" && (
                  <motion.div
                    initial={{ scale: 0.95, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="bg-white/20 backdrop-blur-sm rounded-xl p-4 border-2 border-white/30"
                  >
                    <p className="text-white font-semibold text-sm mb-2">
                      💡 Pro Tip
                    </p>
                    <p className="text-white/90 text-sm">
                      Upgrade to an annual plan and save 17%! Plus, get unlimited workflows
                      and priority support.
                    </p>
                  </motion.div>
                )}
              </div>
            </div>
          </div>

          {/* Animated Background Pattern */}
          <div className="absolute inset-0 opacity-10 pointer-events-none">
            <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent" />
            <motion.div
              animate={{
                scale: [1, 1.2, 1],
                rotate: [0, 90, 0],
              }}
              transition={{
                duration: 20,
                repeat: Infinity,
                ease: "linear",
              }}
              className="absolute -top-1/2 -right-1/2 w-full h-full bg-white/5 rounded-full blur-3xl"
            />
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
