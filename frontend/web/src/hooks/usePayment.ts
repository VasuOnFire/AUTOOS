import { useEffect, useState } from 'react';
import {
  usePaymentStore,
  Subscription,
  TrialStatus,
  PricingTier,
  PaymentHistory,
  UsageStats,
  QRPayment,
} from '@/store/paymentStore';

/**
 * Hook for subscription management
 * Provides subscription data and actions
 */
export function useSubscription() {
  const {
    subscription,
    isLoading,
    error,
    fetchSubscription,
    subscribe,
    upgradeSubscription,
    downgradeSubscription,
    cancelSubscription,
    updatePaymentMethod,
    clearError,
  } = usePaymentStore();

  // Fetch subscription on mount
  useEffect(() => {
    fetchSubscription();
  }, [fetchSubscription]);

  return {
    subscription,
    isLoading,
    error,
    subscribe,
    upgradeSubscription,
    downgradeSubscription,
    cancelSubscription,
    updatePaymentMethod,
    clearError,
  };
}

/**
 * Hook for free trial management
 * Provides trial status and actions
 */
export function useTrial() {
  const {
    trialStatus,
    isLoading,
    error,
    fetchTrialStatus,
    startFreeTrial,
    clearError,
  } = usePaymentStore();

  // Fetch trial status on mount
  useEffect(() => {
    fetchTrialStatus();
  }, [fetchTrialStatus]);

  // Calculate urgency level based on days remaining
  const urgency = trialStatus
    ? trialStatus.days_remaining > 7
      ? 'normal'
      : trialStatus.days_remaining > 3
      ? 'warning'
      : 'critical'
    : 'normal';

  // Calculate credits urgency
  const creditsPercentage = trialStatus
    ? (trialStatus.credits_remaining / trialStatus.credits_total) * 100
    : 100;

  const creditsUrgency =
    creditsPercentage > 50 ? 'normal' : creditsPercentage > 20 ? 'warning' : 'critical';

  return {
    trialStatus,
    isLoading,
    error,
    urgency,
    creditsUrgency,
    creditsPercentage,
    startFreeTrial,
    clearError,
  };
}

/**
 * Hook for pricing tiers
 * Provides pricing information
 */
export function usePricing() {
  const { pricingTiers, isLoading, error, fetchPricingTiers, clearError } =
    usePaymentStore();

  // Fetch pricing tiers on mount
  useEffect(() => {
    if (pricingTiers.length === 0) {
      fetchPricingTiers();
    }
  }, [pricingTiers.length, fetchPricingTiers]);

  return {
    pricingTiers,
    isLoading,
    error,
    clearError,
  };
}

/**
 * Hook for payment history
 * Provides billing history and invoice access
 */
export function usePaymentHistory() {
  const { paymentHistory, isLoading, error, fetchPaymentHistory, clearError } =
    usePaymentStore();

  // Fetch payment history on mount
  useEffect(() => {
    fetchPaymentHistory();
  }, [fetchPaymentHistory]);

  return {
    paymentHistory,
    isLoading,
    error,
    clearError,
  };
}

/**
 * Hook for usage statistics
 * Provides current usage data and limits
 */
export function useUsage() {
  const { usageStats, isLoading, error, fetchUsageStats, clearError } =
    usePaymentStore();

  // Fetch usage stats on mount
  useEffect(() => {
    fetchUsageStats();
  }, [fetchUsageStats]);

  // Calculate usage percentages
  const workflowsPercentage =
    usageStats && typeof usageStats.workflows_limit === 'number'
      ? (usageStats.workflows_this_month / usageStats.workflows_limit) * 100
      : 0;

  const agentsPercentage =
    usageStats && typeof usageStats.agents_limit === 'number'
      ? (usageStats.agents_active / usageStats.agents_limit) * 100
      : 0;

  const storagePercentage =
    usageStats && typeof usageStats.storage_limit_gb === 'number'
      ? (usageStats.storage_used_gb / usageStats.storage_limit_gb) * 100
      : 0;

  // Determine if approaching limits
  const isApproachingWorkflowLimit = workflowsPercentage > 80;
  const isApproachingAgentLimit = agentsPercentage > 80;
  const isApproachingStorageLimit = storagePercentage > 80;

  return {
    usageStats,
    isLoading,
    error,
    workflowsPercentage,
    agentsPercentage,
    storagePercentage,
    isApproachingWorkflowLimit,
    isApproachingAgentLimit,
    isApproachingStorageLimit,
    clearError,
  };
}

/**
 * Hook for QR code payment flow
 * Provides QR code generation and status checking
 */
export function useQRPayment() {
  const {
    qrPayment,
    isLoading,
    error,
    generateQRCode,
    checkQRPaymentStatus,
    clearQRPayment,
    clearError,
  } = usePaymentStore();

  const [isChecking, setIsChecking] = useState(false);
  const [checkInterval, setCheckInterval] = useState<NodeJS.Timeout | null>(null);

  // Start checking payment status every 3 seconds
  const startStatusChecking = (payment_id: string) => {
    if (checkInterval) {
      clearInterval(checkInterval);
    }

    const interval = setInterval(async () => {
      setIsChecking(true);
      try {
        const status = await checkQRPaymentStatus(payment_id);
        
        // Stop checking if payment is completed, failed, or expired
        if (status !== 'pending') {
          stopStatusChecking();
        }
      } catch (error) {
        console.error('Error checking payment status:', error);
      } finally {
        setIsChecking(false);
      }
    }, 3000); // Check every 3 seconds

    setCheckInterval(interval);
  };

  // Stop checking payment status
  const stopStatusChecking = () => {
    if (checkInterval) {
      clearInterval(checkInterval);
      setCheckInterval(null);
    }
    setIsChecking(false);
  };

  // Generate QR code and start checking
  const generateAndCheck = async (data: {
    amount: number;
    currency: string;
    plan_id: string;
    billing_cycle: string;
  }) => {
    try {
      const payment = await generateQRCode(data);
      startStatusChecking(payment.payment_id);
      return payment;
    } catch (error) {
      throw error;
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopStatusChecking();
    };
  }, []);

  return {
    qrPayment,
    isLoading,
    isChecking,
    error,
    generateQRCode: generateAndCheck,
    checkQRPaymentStatus,
    startStatusChecking,
    stopStatusChecking,
    clearQRPayment,
    clearError,
  };
}
