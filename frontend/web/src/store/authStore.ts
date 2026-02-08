import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export interface User {
  user_id: string;
  email: string;
  username: string;
  full_name: string;
  role: 'student' | 'employee' | 'professional' | 'enterprise' | 'admin';
  is_verified: boolean;
  mfa_enabled: boolean;
  created_at: string;
  last_login?: string;
  organization?: string;
  student_id?: string;
  employee_id?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface MFASetup {
  secret: string;
  qr_code: string;
  backup_codes: string[];
}

interface AuthStore {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  mfaRequired: boolean;
  mfaSetup: MFASetup | null;

  // Actions
  signIn: (email: string, password: string) => Promise<{ mfa_required?: boolean }>;
  signInWithMFA: (email: string, password: string, mfaCode: string) => Promise<void>;
  signUp: (data: {
    email: string;
    username: string;
    password: string;
    full_name: string;
    role: string;
    organization?: string;
    student_id?: string;
    employee_id?: string;
  }) => Promise<void>;
  signOut: () => Promise<void>;
  refreshToken: () => Promise<void>;
  getCurrentUser: () => Promise<void>;
  verifyEmail: (token: string) => Promise<void>;
  resendVerification: () => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (token: string, newPassword: string) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  setupMFA: () => Promise<MFASetup>;
  verifyMFA: (code: string) => Promise<void>;
  disableMFA: (code: string) => Promise<void>;
  getBackupCodes: () => Promise<string[]>;
  signInWithOAuth: (provider: string) => void;
  clearError: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const useAuthStore = create<AuthStore>()(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        mfaRequired: false,
        mfaSetup: null,

        signIn: async (email: string, password: string) => {
          set({ isLoading: true, error: null, mfaRequired: false });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/signin`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Sign in failed');
            }

            const data = await response.json();

            if (data.mfa_required) {
              set({ mfaRequired: true, isLoading: false });
              return { mfa_required: true };
            }

            set({
              tokens: data.tokens,
              user: data.user,
              isAuthenticated: true,
              isLoading: false,
            });

            return {};
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Sign in failed',
              isLoading: false,
            });
            throw error;
          }
        },

        signInWithMFA: async (email: string, password: string, mfaCode: string) => {
          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/signin`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email, password, mfa_code: mfaCode }),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'MFA verification failed');
            }

            const data = await response.json();

            set({
              tokens: data.tokens,
              user: data.user,
              isAuthenticated: true,
              mfaRequired: false,
              isLoading: false,
            });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'MFA verification failed',
              isLoading: false,
            });
            throw error;
          }
        },

        signUp: async (data: {
          email: string;
          username: string;
          password: string;
          full_name: string;
          role: string;
          organization?: string;
          student_id?: string;
          employee_id?: string;
        }) => {
          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/signup`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(data),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Sign up failed');
            }

            const result = await response.json();

            set({
              user: result.user,
              tokens: result.tokens,
              isAuthenticated: true,
              isLoading: false,
            });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Sign up failed',
              isLoading: false,
            });
            throw error;
          }
        },

        signOut: async () => {
          set({ isLoading: true, error: null });

          try {
            const { tokens } = get();
            if (tokens) {
              await fetch(`${API_BASE_URL}/auth/signout`, {
                method: 'POST',
                headers: {
                  'Authorization': `Bearer ${tokens.access_token}`,
                },
              });
            }

            set({
              user: null,
              tokens: null,
              isAuthenticated: false,
              mfaRequired: false,
              mfaSetup: null,
              isLoading: false,
            });
          } catch (error) {
            // Clear local state even if API call fails
            set({
              user: null,
              tokens: null,
              isAuthenticated: false,
              mfaRequired: false,
              mfaSetup: null,
              error: error instanceof Error ? error.message : 'Sign out failed',
              isLoading: false,
            });
          }
        },

        refreshToken: async () => {
          const { tokens } = get();
          if (!tokens?.refresh_token) return;

          try {
            const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ refresh_token: tokens.refresh_token }),
            });

            if (!response.ok) {
              throw new Error('Token refresh failed');
            }

            const data = await response.json();

            set({
              tokens: data.tokens,
            });
          } catch (error) {
            // Token refresh failed, sign out
            set({
              user: null,
              tokens: null,
              isAuthenticated: false,
              error: 'Session expired. Please sign in again.',
            });
          }
        },

        getCurrentUser: async () => {
          const { tokens } = get();
          if (!tokens) return;

          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/me`, {
              headers: {
                'Authorization': `Bearer ${tokens.access_token}`,
              },
            });

            if (!response.ok) {
              throw new Error('Failed to fetch user');
            }

            const data = await response.json();

            set({
              user: data.user,
              isLoading: false,
            });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to fetch user',
              isLoading: false,
            });
          }
        },

        verifyEmail: async (token: string) => {
          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/verify-email`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ token }),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Email verification failed');
            }

            const data = await response.json();

            set((state: AuthStore) => ({
              user: state.user ? { ...state.user, is_verified: true } : null,
              isLoading: false,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Email verification failed',
              isLoading: false,
            });
            throw error;
          }
        },

        resendVerification: async () => {
          const { tokens } = get();
          if (!tokens) throw new Error('Not authenticated');

          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/resend-verification`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${tokens.access_token}`,
              },
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Failed to resend verification');
            }

            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to resend verification',
              isLoading: false,
            });
            throw error;
          }
        },

        forgotPassword: async (email: string) => {
          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email }),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Failed to send reset email');
            }

            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to send reset email',
              isLoading: false,
            });
            throw error;
          }
        },

        resetPassword: async (token: string, newPassword: string) => {
          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ token, new_password: newPassword }),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Password reset failed');
            }

            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Password reset failed',
              isLoading: false,
            });
            throw error;
          }
        },

        changePassword: async (currentPassword: string, newPassword: string) => {
          const { tokens } = get();
          if (!tokens) throw new Error('Not authenticated');

          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/change-password`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${tokens.access_token}`,
              },
              body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword,
              }),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Password change failed');
            }

            set({ isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Password change failed',
              isLoading: false,
            });
            throw error;
          }
        },

        updateProfile: async (data: Partial<User>) => {
          const { tokens } = get();
          if (!tokens) throw new Error('Not authenticated');

          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/profile`, {
              method: 'PATCH',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${tokens.access_token}`,
              },
              body: JSON.stringify(data),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Profile update failed');
            }

            const result = await response.json();

            set((state: AuthStore) => ({
              user: state.user ? { ...state.user, ...result.user } : null,
              isLoading: false,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Profile update failed',
              isLoading: false,
            });
            throw error;
          }
        },

        setupMFA: async () => {
          const { tokens } = get();
          if (!tokens) throw new Error('Not authenticated');

          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/mfa/setup`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${tokens.access_token}`,
              },
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'MFA setup failed');
            }

            const data = await response.json();

            set({
              mfaSetup: data,
              isLoading: false,
            });

            return data;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'MFA setup failed',
              isLoading: false,
            });
            throw error;
          }
        },

        verifyMFA: async (code: string) => {
          const { tokens } = get();
          if (!tokens) throw new Error('Not authenticated');

          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/mfa/verify`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${tokens.access_token}`,
              },
              body: JSON.stringify({ code }),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'MFA verification failed');
            }

            set((state: AuthStore) => ({
              user: state.user ? { ...state.user, mfa_enabled: true } : null,
              mfaSetup: null,
              isLoading: false,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'MFA verification failed',
              isLoading: false,
            });
            throw error;
          }
        },

        disableMFA: async (code: string) => {
          const { tokens } = get();
          if (!tokens) throw new Error('Not authenticated');

          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/mfa/disable`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${tokens.access_token}`,
              },
              body: JSON.stringify({ code }),
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Failed to disable MFA');
            }

            set((state: AuthStore) => ({
              user: state.user ? { ...state.user, mfa_enabled: false } : null,
              isLoading: false,
            }));
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to disable MFA',
              isLoading: false,
            });
            throw error;
          }
        },

        getBackupCodes: async () => {
          const { tokens } = get();
          if (!tokens) throw new Error('Not authenticated');

          set({ isLoading: true, error: null });

          try {
            const response = await fetch(`${API_BASE_URL}/auth/mfa/backup-codes`, {
              headers: {
                'Authorization': `Bearer ${tokens.access_token}`,
              },
            });

            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'Failed to get backup codes');
            }

            const data = await response.json();

            set({ isLoading: false });

            return data.backup_codes;
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Failed to get backup codes',
              isLoading: false,
            });
            throw error;
          }
        },

        signInWithOAuth: (provider: string) => {
          window.location.href = `${API_BASE_URL}/auth/oauth/${provider}/authorize`;
        },

        clearError: () => set({ error: null }),
      }),
      {
        name: 'autoos-auth-store',
        partialize: (state: AuthStore) => ({
          user: state.user,
          tokens: state.tokens,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    )
  )
);

