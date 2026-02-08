"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Crown,
  Calendar,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Zap,
  Users,
  CreditCard,
  XCircle,
  ArrowUpCircle,
  ArrowDownCircle,
  Clock,
  DollarSign,
  Activity,
  Sparkles,
} from "lucide-react";
import toast from "react-hot-toast";

interface Subscription {
  subscription_id: string;
  user_id: string;
  tier: string;
  status: string;
  billing_cycle: string;
  subscription_start_date: string;
  subscription_end_date: string;
  next_billing_date: string;
  amount: number;
  currency: string;
  auto_renew: boolean;
  payment_method: string;
}

interface TrialStatus {
  is_active: boolean;
  trial_start_date: string;
  trial_end_date: string;
  days_remaining: number;
  credits_remaining: number;
  initial_credits: number;
}

interface UsageStats {
  workflows_used: number;
  workflows_limit: number;
  agents_used: number;
  agents_limit: number;
  credits_used: number;
  credits_limit: number;
  period_start: string;
  period_end: string;
}

interface SubscriptionManagerProps {
  onUpgrade?: (planId: string) => void;
  onDowngrade?: (planId: string) => void;
  onCancel?: () => void;
}

export default function SubscriptionManager({
  onUpgrade,
  onDowngrade,
  onCancel,
}: SubscriptionManagerProps) {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [trialStatus, setTrialStatus] = useState<TrialStatus | null>(null);
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [showCancelModal, setShowCancelModal] = useState(false);

  useEffect(() => {
    fetchSubscriptionData();
  }, []);

  const fetchSubscriptionData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const headers = {
        Authorization: `Bearer ${token}`,
      };

      // Fetch subscription
      const subResponse = await fetch("/api/payments/subscription", {
        headers,
      });
      if (subResponse.ok) {
        const subData = await subResponse.json();
        setSubscription(subData);
      }

      // Fetch trial status
      const trialResponse = await fetch("/api/payments/trial-status", {
        headers,
      });
      if (trialResponse.ok) {
        const trialData = await trialResponse.json();
        setTrialStatus(trialData);
      }

      // Fetch usage stats
      const usageResponse = await fetch("/api/payments/usage", {
        headers,
      });
      if (usageResponse.ok) {
        const usageData = await usageResponse.json();
        setUsageStats(usageData);
      }
    } catch (error: any) {
      toast.error("Failed to load subscription data");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (planId: string) => {
    setActionLoading("upgrade");
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/payments/upgrade", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ plan_id: planId }),
      });

      if (!response.ok) {
        throw new Error("Failed to upgrade subscription");
      }

      toast.success("Subscription upgraded successfully!");
      await fetchSubscriptionData();

      if (onUpgrade) {
        onUpgrade(planId);
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to upgrade subscription");
    } finally {
      setActionLoading(null);
    }
  };

  const handleDowngrade = async (planId: string) => {
    setActionLoading("downgrade");
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/payments/downgrade", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ plan_id: planId }),
      });

      if (!response.ok) {
        throw new Error("Failed to downgrade subscription");
      }

      toast.success("Subscription downgraded successfully!");
      await fetchSubscriptionData();

      if (onDowngrade) {
        onDowngrade(planId);
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to downgrade subscription");
    } finally {
      setActionLoading(null);
    }
  };

  const handleCancelSubscription = async () => {
    setActionLoading("cancel");
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/payments/cancel-subscription", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to cancel subscription");
      }

      toast.success("Subscription cancelled successfully");
      setShowCancelModal(false);
      await fetchSubscriptionData();

      if (onCancel) {
        onCancel();
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to cancel subscription");
    } finally {
      setActionLoading(null);
    }
  };

  const getUsagePercentage = (used: number, limit: number) => {
    if (limit === 0) return 0;
    return Math.min((used / limit) * 100, 100);
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return "text-red-600 dark:text-red-400";
    if (percentage >= 75) return "text-yellow-600 dark:text-yellow-400";
    return "text-green-600 dark:text-green-400";
  };

  const getProgressBarColor = (percentage: number) => {
    if (percentage >= 90) return "bg-red-600";
    if (percentage >= 75) return "bg-yellow-600";
    return "bg-green-600";
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const getPlanIcon = (tier: string) => {
    switch (tier?.toLowerCase()) {
      case "trial":
        return <Sparkles className="w-6 h-6" />;
      case "student":
        return <Zap className="w-6 h-6" />;
      case "employee":
        return <Users className="w-6 h-6" />;
      case "professional":
        return <Crown className="w-6 h-6" />;
      default:
        return <Activity className="w-6 h-6" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-600 dark:text-gray-400">
            Loading subscription data...
          </p>
        </div>
      </div>
    );
  }

  const isOnTrial = trialStatus?.is_active;
  const currentTier = subscription?.tier || "trial";

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
          Subscription Management
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Manage your subscription, view usage, and upgrade your plan
        </p>
      </div>

      {/* Trial Status Banner */}
      {isOnTrial && trialStatus && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl shadow-xl p-6 text-white"
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-2xl font-bold mb-2">
                  Free Trial Active
                </h3>
                <p className="text-green-100 mb-4">
                  You're currently on a 30-day free trial. No credit card required!
                </p>
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <Clock className="w-5 h-5" />
                    <span className="font-semibold">
                      {trialStatus.days_remaining} days remaining
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Zap className="w-5 h-5" />
                    <span className="font-semibold">
                      {trialStatus.credits_remaining} / {trialStatus.initial_credits} credits left
                    </span>
                  </div>
                </div>
                <p className="text-sm text-green-100 mt-2">
                  Trial expires on {formatDate(trialStatus.trial_end_date)}
                </p>
              </div>
            </div>
            <button
              onClick={() => onUpgrade && onUpgrade("student")}
              className="bg-white text-green-600 px-6 py-3 rounded-lg font-semibold hover:bg-green-50 transition-colors flex items-center gap-2"
            >
              <ArrowUpCircle className="w-5 h-5" />
              Upgrade Now
            </button>
          </div>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Current Subscription Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6"
        >
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className={`w-14 h-14 rounded-lg flex items-center justify-center ${
                isOnTrial
                  ? "bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400"
                  : "bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400"
              }`}>
                {getPlanIcon(currentTier)}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white capitalize">
                  {currentTier} Plan
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  {subscription?.status === "active" ? "Active" : "Inactive"}
                </p>
              </div>
            </div>
            {subscription?.status === "active" && (
              <div className="flex items-center gap-2 px-4 py-2 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-lg">
                <CheckCircle className="w-5 h-5" />
                <span className="font-semibold">Active</span>
              </div>
            )}
          </div>

          {/* Billing Information */}
          {subscription && !isOnTrial && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="flex items-start gap-3">
                <Calendar className="w-5 h-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Billing Cycle
                  </p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                    {subscription.billing_cycle}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <DollarSign className="w-5 h-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Next Payment
                  </p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {subscription.currency} {subscription.amount.toFixed(2)}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    on {formatDate(subscription.next_billing_date)}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <CreditCard className="w-5 h-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Payment Method
                  </p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                    {subscription.payment_method}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <TrendingUp className="w-5 h-5 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Auto Renewal
                  </p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {subscription.auto_renew ? "Enabled" : "Disabled"}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4">
            {isOnTrial ? (
              <button
                onClick={() => onUpgrade && onUpgrade("student")}
                disabled={actionLoading === "upgrade"}
                className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {actionLoading === "upgrade" ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Upgrading...
                  </>
                ) : (
                  <>
                    <ArrowUpCircle className="w-5 h-5" />
                    Upgrade from Trial
                  </>
                )}
              </button>
            ) : (
              <>
                <button
                  onClick={() => onUpgrade && onUpgrade("professional")}
                  disabled={actionLoading === "upgrade"}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {actionLoading === "upgrade" ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Upgrading...
                    </>
                  ) : (
                    <>
                      <ArrowUpCircle className="w-5 h-5" />
                      Upgrade Plan
                    </>
                  )}
                </button>
                <button
                  onClick={() => onDowngrade && onDowngrade("student")}
                  disabled={actionLoading === "downgrade"}
                  className="flex-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-6 py-3 rounded-lg font-semibold hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {actionLoading === "downgrade" ? (
                    <>
                      <div className="w-5 h-5 border-2 border-gray-700 dark:border-gray-300 border-t-transparent rounded-full animate-spin" />
                      Downgrading...
                    </>
                  ) : (
                    <>
                      <ArrowDownCircle className="w-5 h-5" />
                      Downgrade Plan
                    </>
                  )}
                </button>
              </>
            )}
            {!isOnTrial && subscription?.status === "active" && (
              <button
                onClick={() => setShowCancelModal(true)}
                className="px-6 py-3 border border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 rounded-lg font-semibold hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors flex items-center gap-2"
              >
                <XCircle className="w-5 h-5" />
                Cancel Subscription
              </button>
            )}
          </div>
        </motion.div>

        {/* Usage Statistics Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6"
        >
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
            Usage Statistics
          </h3>

          {usageStats ? (
            <div className="space-y-6">
              {/* Workflows Usage */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Workflows
                    </span>
                  </div>
                  <span className={`text-sm font-semibold ${getUsageColor(
                    getUsagePercentage(usageStats.workflows_used, usageStats.workflows_limit)
                  )}`}>
                    {usageStats.workflows_used} / {usageStats.workflows_limit === -1 ? "∞" : usageStats.workflows_limit}
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${getProgressBarColor(
                      getUsagePercentage(usageStats.workflows_used, usageStats.workflows_limit)
                    )}`}
                    style={{
                      width: `${getUsagePercentage(usageStats.workflows_used, usageStats.workflows_limit)}%`,
                    }}
                  />
                </div>
              </div>

              {/* Agents Usage */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Users className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Concurrent Agents
                    </span>
                  </div>
                  <span className={`text-sm font-semibold ${getUsageColor(
                    getUsagePercentage(usageStats.agents_used, usageStats.agents_limit)
                  )}`}>
                    {usageStats.agents_used} / {usageStats.agents_limit === -1 ? "∞" : usageStats.agents_limit}
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${getProgressBarColor(
                      getUsagePercentage(usageStats.agents_used, usageStats.agents_limit)
                    )}`}
                    style={{
                      width: `${getUsagePercentage(usageStats.agents_used, usageStats.agents_limit)}%`,
                    }}
                  />
                </div>
              </div>

              {/* Credits Usage (for trial users) */}
              {isOnTrial && trialStatus && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Zap className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Trial Credits
                      </span>
                    </div>
                    <span className={`text-sm font-semibold ${getUsageColor(
                      getUsagePercentage(
                        trialStatus.initial_credits - trialStatus.credits_remaining,
                        trialStatus.initial_credits
                      )
                    )}`}>
                      {trialStatus.credits_remaining} / {trialStatus.initial_credits}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${getProgressBarColor(
                        getUsagePercentage(
                          trialStatus.initial_credits - trialStatus.credits_remaining,
                          trialStatus.initial_credits
                        )
                      )}`}
                      style={{
                        width: `${getUsagePercentage(
                          trialStatus.initial_credits - trialStatus.credits_remaining,
                          trialStatus.initial_credits
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Usage Period */}
              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                  Current Period
                </p>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {formatDate(usageStats.period_start)} - {formatDate(usageStats.period_end)}
                </p>
              </div>

              {/* Usage Warnings */}
              {getUsagePercentage(usageStats.workflows_used, usageStats.workflows_limit) >= 90 && (
                <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-600 dark:text-red-400">
                    You're approaching your workflow limit. Consider upgrading your plan.
                  </p>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-600 dark:text-gray-400">
              No usage data available
            </p>
          )}
        </motion.div>
      </div>

      {/* Cancel Subscription Modal */}
      {showCancelModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full p-6"
          >
            <div className="flex items-start gap-4 mb-6">
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-400" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  Cancel Subscription
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Are you sure you want to cancel your subscription? You'll lose access to premium features at the end of your billing period.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setShowCancelModal(false)}
                disabled={actionLoading === "cancel"}
                className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Keep Subscription
              </button>
              <button
                onClick={handleCancelSubscription}
                disabled={actionLoading === "cancel"}
                className="flex-1 bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {actionLoading === "cancel" ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Cancelling...
                  </>
                ) : (
                  "Yes, Cancel"
                )}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
