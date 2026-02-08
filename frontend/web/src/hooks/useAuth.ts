import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore, User, MFASetup } from '@/store/authStore';

/**
 * Main authentication hook
 * Provides access to auth state and all authentication actions
 */
export function useAuth() {
  const {
    user,
    tokens,
    isAuthenticated,
    isLoading,
    error,
    mfaRequired,
    mfaSetup,
    signIn,
    signInWithMFA,
    signUp,
    signOut,
    refreshToken,
    getCurrentUser,
    verifyEmail,
    resendVerification,
    forgotPassword,
    resetPassword,
    changePassword,
    updateProfile,
    setupMFA,
    verifyMFA,
    disableMFA,
    getBackupCodes,
    signInWithOAuth,
    clearError,
  } = useAuthStore();

  // Auto-refresh token before expiration
  useEffect(() => {
    if (!tokens) return;

    const refreshInterval = setInterval(() => {
      refreshToken();
    }, 14 * 60 * 1000); // Refresh every 14 minutes (tokens expire in 15 minutes)

    return () => clearInterval(refreshInterval);
  }, [tokens, refreshToken]);

  // Fetch current user on mount if authenticated
  useEffect(() => {
    if (isAuthenticated && !user) {
      getCurrentUser();
    }
  }, [isAuthenticated, user, getCurrentUser]);

  return {
    user,
    tokens,
    isAuthenticated,
    isLoading,
    error,
    mfaRequired,
    mfaSetup,
    signIn,
    signInWithMFA,
    signUp,
    signOut,
    refreshToken,
    getCurrentUser,
    verifyEmail,
    resendVerification,
    forgotPassword,
    resetPassword,
    changePassword,
    updateProfile,
    setupMFA,
    verifyMFA,
    disableMFA,
    getBackupCodes,
    signInWithOAuth,
    clearError,
  };
}

/**
 * Hook for protected routes
 * Redirects to sign-in page if not authenticated
 */
export function useRequireAuth(redirectTo: string = '/auth/signin') {
  const router = useRouter();
  const { isAuthenticated, isLoading, user } = useAuthStore();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(redirectTo);
    }
  }, [isAuthenticated, isLoading, router, redirectTo]);

  return {
    isAuthenticated,
    isLoading,
    user,
  };
}

/**
 * Hook for accessing current user data
 * Returns null if not authenticated
 */
export function useUser(): User | null {
  const { user, isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return null;
  }

  return user;
}

/**
 * Hook for MFA operations
 * Provides MFA-specific state and actions
 */
export function useMFA() {
  const {
    user,
    mfaSetup,
    isLoading,
    error,
    setupMFA,
    verifyMFA,
    disableMFA,
    getBackupCodes,
    clearError,
  } = useAuthStore();

  const isMFAEnabled = user?.mfa_enabled || false;

  return {
    isMFAEnabled,
    mfaSetup,
    isLoading,
    error,
    setupMFA,
    verifyMFA,
    disableMFA,
    getBackupCodes,
    clearError,
  };
}
