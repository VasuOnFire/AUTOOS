import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export interface PricingTier {
  id: string;
  name: string;
  price_monthly: number;
  price_annual: number;
  features: string[];
  limits: {
    workflows_per_month: number | 'unlimited';
    concurrent_agents: number | 'unlimited';
    storage_gb: number | 'unlimited';
  };
  is_popular?: boolean;
}

export interface Subscription {
  subscription_id: string;
  user_id: string;
  tier: string;
  status: 'active' | 'cancelled' | 'past_due' | 'trialing';
  billing_cycle: 'monthly' | 'annual';
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  payment_method?: {
    type: 'card' | 'qr_code';
    last4?: string;
    brand?: string;
    exp_month?: number;
    exp_year?: number;
  };
  amount: number;
  currency: string;
}

export interface TrialStatus {
  is_active: boolean;
  trial_start_date: string;
  trial_end_date: string;
  days_remaining: number;
  credits_remaining: number;
  credits_total: number;
  workflows_used: number;
  workflows_limit: number;
}

export interface PaymentHistory {
  payment_id: string;
  amount: number;
  currency: string;
  status: 'succeeded' | 'pending' | 'failed';
  payment_method: 'card' | 'qr_code';
  created_at: string;
  description: string;
  invoice_url?: string;
}

export interface UsageStats {
  workflows_this_month: number;
  workflows_limit: number | 'unlimited';
  agents_active: number;
  agents_limit: number | 'unlimited';
  storage_used_gb: number;
  storage_limit_gb: number | 'unlimited';
  cost_this_month: number;
}

export interface QRPayment {
  payment_id: string;
  qr_code_data: string;
  qr_code_image: string;
  upi_id: string;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed' | 'expired';
  expires_at: string;
  created_at: string;
}

interface PaymentStore {
  subscription: Subscription | null;
  trialStatus: TrialStatus | null;
  pricingTiers: PricingTier[];
  paymentHistory: PaymentHistory[];
  usageStats: UsageStats | null;
  qrPayment: QRPayment | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchPricingTiers: () => Promise<void>;
  fetchSubscription: () => Promise<void>;
  fetchTrialStatus: () => Promise<void>;
  fetchPaymentHistory: () => Promise<void>;
  fetchUsageStats: () => Promise<void>;
  startFreeTrial: () => Promise<void>;
  subscribe: (data: {
    tier: string;
    billing_cycle: 'monthly' | 'annual';
    payment_method_id?: string;
  }) => Promise<void>;
  upgradeSubscription: (tier: string) => Promise<void>;
  downgradeSubscription: (tier: string) => Promise<void>;
  cancelSubscription: () => Promise<void>;
  updatePaymentMethod: (payment_method_id: string) => Promise<void>;
  generateQRCode: (data: {
    amount: number;
    currency: string;
    plan_id: string;
    billing_cycle: string;
  }) => Promise<QRPayment>;
  checkQRPaymentStatus: (payment_id: string) => Promise<'pending' | 'completed' | 'failed' | 'expired'>;
  clearQRPayment: () => void;
  clearError: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const usePaymentStore = create<PaymentStore>()(
  devtools(
    persist(
      (set: any, get: any) => ({
        subscription: null as Subscription | null,
        trialStatus: null as TrialStatus | null,
        pricingTiers: [] as PricingTier[],
        paymentHistory: [] as PaymentHistory[],
        usageStats: null as UsageStats | null,
        qrPayment: null as QRPayment | null,
        isLoading: false as boolean,
        error: null as string | null,

        fetchPricingTiers: async () => {
          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/payments/pricing`);

            if (!response.ok) {
              throw new Error('Failed to fetch pricing tiers');
            }

            const data = await response.json();

            set({
              pricingTiers: data.tiers || [],
              isLoading: false,
            });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch pricing',
              isLoading: false,
            });
          }
        },

        fetchSubscription: async () => {
          try {
            const token = localStorage.getItem('auth_token');
            if (!token) return;

            const response = await fetch(`${API_BASE_URL}/payments/subscription`, {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            });

            if (!response.ok) {
              throw new Error('Failed to fetch subscription');
            }

            const data = await response.json();

            set({
              subscription: data.subscription || null,
            });
          } catch (error) {
            console.error('Error fetching subscription:', error);
          }
        },

        fetchTrialStatus: async () => {
          try {
            const token = localStorage.getItem('auth_token');
            if (!token) return;

            const response = await fetch(`${API_BASE_URL}/payments/trial-status`, {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            });

            if (!response.ok) {
              throw new Error('Failed to fetch trial status');
            }

            const data = await response.json();

            set({
              trialStatus: data.trial || null,
            });
          } catch (error) {
            console.error('Error fetching trial status:', error);
          }
        },

        fetchPaymentHistory: async () => {
          set({ isLoading: true, error: null });

          try {
            const token = localStorage.getItem('auth_token');
            if (!token) throw new Error('Not authenticated');

            const response = await fetch(`${API_BASE_URL}/payments/history`, {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            });

            if (!response.ok) {
              throw new Error('Failed to fetch payment history');
            }

            const data = await response.json();

            set({
              paymentHistory: data.payments || [],
              isLoading: false,
            });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch payment history',
              isLoading: false,
            });
          }
        },

        fetchUsageStats: async () => {
          try {
            const token = localStorage.getItem('auth_token');
            if (!token) return;

            const response = await fetch(`${API_BASE_URL}/payments/usage`, {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            });

            if (!response.ok) {
              throw new Error('Failed to fetch usage stats');
            }

            const data = await response.json();

            set({
              usageStats: data.usage || null,
            });
          } catch (error) {
            console.error('Error fetching usage stats:', error);
          }
        },

        startFreeTrial: async () => {
          set({ isLoading: true, error: null });

          try {
            const token = localStorage.getItem('auth_token');
            if (!token) throw new Error('Not authenticated');

            const response = await fetch(`${API_BASE_URL}/payments/start-trial`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Failed to start trial');
            }

            const data = await response.json();

            set({
              trialStatus: data.trial,
              isLoading: false,
            });

            // Refresh subscription data
            await get().fetchSubscription();
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to start trial',
              isLoading: false,
            });
            throw error;
          }
        },

        subscribe: async (data: {
          tier: string;
          billing_cycle: 'monthly' | 'annual';
          payment_method_id?: string;
        }) => {
          set({ isLoading: true, error: null });

          try {
            const token = localStorage.getItem('auth_token');
            if (!token) throw new Error('Not authenticated');

            const response = await fetch(`${API_BASE_URL}/payments/subscribe`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
              },
              body: JSON.stringify(data),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Subscription failed');
            }

            const result = await response.json();

            set({
              subscription: result.subscription,
              isLoading: false,
            });

            // Refresh trial status (should be inactive now)
            await get().fetchTrialStatus();
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Subscription failed',
              isLoading: false,
            });
            throw error;
          }
        },

        upgradeSubscription: async (tier: string) => {
          set({ isLoading: true, error: null });

          try {
            const token = localStorage.getItem('auth_token');
            if (!token) throw new Error('Not authenticated');

            const response = await fetch(`${API_BASE_URL}/payments/upgrade`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
              },
              body: JSON.stringify({ tier }),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Upgrade failed');
            }

            const result = await response.json();

            set({
              subscription: result.subscription,
              isLoading: false,
            });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Upgrade failed',
              isLoading: false,
            });
            throw error;
          }
        },

        downgradeSubscription: async (tier: string) => {
          set({ isLoading: true, error: null });

          try {
            const token = localStorage.getItem('auth_token');
            if (!token) throw new Error('Not authenticated');

            const response = await fetch(`${API_BASE_URL}/payments/downgrade`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
              },
              body: JSON.stringify({ tier }),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Downgrade failed');
            }

            const result = await response.json();

            set({
              subscription: result.subscription,
              isLoading: false,
            });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Downgrade failed',
              isLoading: false,
            });
            throw error;
          }
        },

        cancelSubscription: async () => {
          set({ isLoading: true, error: null });

          try {
            const token = localStorage.getItem('auth_token');
            if (!token) throw new Error('Not authenticated');

            const response = await fetch(`${API_BASE_URL}/payments/cancel-subscription`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Cancellation failed');
            }

            const result = await response.json();

            set({
              subscription: result.subscription,
              isLoading: false,
            });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Cancellation failed',
              isLoading: false,
            });
            throw error;
          }
        },

        updatePaymentMethod: async (payment_method_id: string) => {
          set({ isLoading: true, error: null });

          try {
            const token = localStorage.getItem('auth_token');
            if (!token) throw new Error('Not authenticated');

            const response = await fetch(`${API_BASE_URL}/payments/update-payment-method`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
              },
              body: JSON.stringify({ payment_method_id }),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Failed to update payment method');
            }

            set({ isLoading: false });

            // Refresh subscription data
            await get().fetchSubscription();
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to update payment method',
              isLoading: false,
            });
            throw error;
          }
        },

        generateQRCode: async (data: {
          amount: number;
          currency: string;
          plan_id: string;
          billing_cycle: string;
        }) => {
          set({ isLoading: true, error: null });

          try {
            const token = localStorage.getItem('auth_token');
            if (!token) throw new Error('Not authenticated');

            const response = await fetch(`${API_BASE_URL}/payments/qr-code`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
              },
              body: JSON.stringify(data),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Failed to generate QR code');
            }

            const result = await response.json();

            set({
              qrPayment: result.payment,
              isLoading: false,
            });

            return result.payment;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to generate QR code',
              isLoading: false,
            });
            throw error;
          }
        },

        checkQRPaymentStatus: async (payment_id: string) => {
          try {
            const token = localStorage.getItem('auth_token');
            if (!token) throw new Error('Not authenticated');

            const response = await fetch(
              `${API_BASE_URL}/payments/qr-code/${payment_id}/status`,
              {
                headers: {
                  'Authorization': `Bearer ${token}`,
                },
              }
            );

            if (!response.ok) {
              throw new Error('Failed to check payment status');
            }

            const data = await response.json();

            // Update QR payment status in store
            set((state: PaymentStore) => ({
              qrPayment: state.qrPayment
                ? { ...state.qrPayment, status: data.status }
                : null,
            }));

            return data.status;
          } catch (error) {
            console.error('Error checking QR payment status:', error);
            throw error;
          }
        },

        clearQRPayment: () => {
          set({ qrPayment: null });
        },

        clearError: () => set({ error: null }),
      }),
      {
        name: 'autoos-payment-store',
        partialize: (state: PaymentStore) => ({
          subscription: state.subscription,
          trialStatus: state.trialStatus,
          pricingTiers: state.pricingTiers,
        }),
      }
    )
  )
);
