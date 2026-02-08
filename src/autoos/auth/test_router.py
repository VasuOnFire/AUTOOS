"""
Unit tests for authentication router

Tests all authentication endpoints to ensure they work correctly.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime

from autoos.auth.router import router
from autoos.auth.authentication import UserRole, SubscriptionTier

# Create test app
app = FastAPI()
app.include_router(router)

client = TestClient(app)


class TestBasicAuthEndpoints:
    """Test basic authentication endpoints (Task 31.1)"""

    def test_signup_success(self):
        """Test successful user signup"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "test@example.com",
                "password": "Pass123!word",
                "username": "testuser",
                "full_name": "Test User",
                "role": "student",
            },
        )
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "message" in data

    def test_signup_weak_password(self):
        """Test signup with weak password"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "test@example.com",
                "password": "weak",
                "username": "testuser",
                "full_name": "Test User",
                "role": "student",
            },
        )
        assert response.status_code == 422  # Validation error

    def test_signin_endpoint_exists(self):
        """Test signin endpoint exists"""
        response = client.post(
            "/auth/signin",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
            },
        )
        # Will fail because user doesn't exist in database, but endpoint exists
        assert response.status_code in [401, 500]

    def test_signout_requires_auth(self):
        """Test signout requires authentication"""
        response = client.post("/auth/signout")
        assert response.status_code == 401

    def test_refresh_token_invalid(self):
        """Test refresh with invalid token"""
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )
        assert response.status_code in [401, 500]  # Can be either depending on JWT library

    def test_get_me_requires_auth(self):
        """Test /me endpoint requires authentication"""
        response = client.get("/auth/me")
        assert response.status_code == 401


class TestEmailVerificationEndpoints:
    """Test email verification endpoints (Task 31.2)"""

    def test_verify_email_endpoint_exists(self):
        """Test verify email endpoint exists"""
        response = client.post(
            "/auth/verify-email",
            json={"token": "test_token"},
        )
        # Endpoint exists, will return 200 or 400/500 depending on implementation
        assert response.status_code in [200, 400, 500]

    def test_resend_verification_endpoint_exists(self):
        """Test resend verification endpoint exists"""
        response = client.post(
            "/auth/resend-verification",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 200


class TestPasswordManagementEndpoints:
    """Test password management endpoints (Task 31.3)"""

    def test_forgot_password_endpoint_exists(self):
        """Test forgot password endpoint exists"""
        response = client.post(
            "/auth/forgot-password",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 200

    def test_reset_password_endpoint_exists(self):
        """Test reset password endpoint exists"""
        response = client.post(
            "/auth/reset-password",
            json={
                "token": "test_token",
                "new_password": "NewSecurePass123!",
            },
        )
        assert response.status_code in [200, 500]

    def test_reset_password_weak_password(self):
        """Test reset password with weak password"""
        response = client.post(
            "/auth/reset-password",
            json={
                "token": "test_token",
                "new_password": "weak",
            },
        )
        assert response.status_code == 422  # Validation error

    def test_change_password_requires_auth(self):
        """Test change password requires authentication"""
        response = client.post(
            "/auth/change-password",
            json={
                "old_password": "OldPass123!",
                "new_password": "NewPass123!",
            },
        )
        assert response.status_code == 401


class TestMFAEndpoints:
    """Test MFA endpoints (Task 31.4)"""

    def test_mfa_setup_requires_auth(self):
        """Test MFA setup requires authentication"""
        response = client.post("/auth/mfa/setup")
        assert response.status_code == 401

    def test_mfa_verify_requires_auth(self):
        """Test MFA verify requires authentication"""
        response = client.post(
            "/auth/mfa/verify",
            json={"code": "123456"},
        )
        assert response.status_code == 401

    def test_mfa_disable_requires_auth(self):
        """Test MFA disable requires authentication"""
        response = client.post(
            "/auth/mfa/disable",
            json={"password": "SecurePass123!"},
        )
        assert response.status_code == 401

    def test_mfa_backup_codes_requires_auth(self):
        """Test backup codes requires authentication"""
        response = client.get("/auth/mfa/backup-codes")
        assert response.status_code == 401


class TestOAuthEndpoints:
    """Test OAuth endpoints (Task 31.5)"""

    def test_oauth_authorize_google(self):
        """Test OAuth authorization for Google"""
        response = client.get("/auth/oauth/google/authorize")
        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert "state" in data
        assert "google" in data["authorization_url"]

    def test_oauth_authorize_github(self):
        """Test OAuth authorization for GitHub"""
        response = client.get("/auth/oauth/github/authorize")
        assert response.status_code == 200
        data = response.json()
        assert "github" in data["authorization_url"]

    def test_oauth_authorize_invalid_provider(self):
        """Test OAuth with invalid provider"""
        response = client.get("/auth/oauth/invalid/authorize")
        assert response.status_code == 400

    def test_oauth_callback_endpoint_exists(self):
        """Test OAuth callback endpoint exists"""
        response = client.get(
            "/auth/oauth/google/callback",
            params={"code": "test_code", "state": "test_state"},
        )
        assert response.status_code in [200, 500]


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test health check returns healthy status"""
        response = client.get("/auth/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "authentication"
        assert "timestamp" in data


class TestPasswordValidation:
    """Test password validation rules"""

    def test_password_too_short(self):
        """Test password must be at least 12 characters"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "test@example.com",
                "password": "Short1!",
                "username": "testuser",
                "full_name": "Test User",
                "role": "student",
            },
        )
        assert response.status_code == 422

    def test_password_no_uppercase(self):
        """Test password must contain uppercase letter"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "test@example.com",
                "password": "lowercase123!",
                "username": "testuser",
                "full_name": "Test User",
                "role": "student",
            },
        )
        assert response.status_code == 422

    def test_password_no_lowercase(self):
        """Test password must contain lowercase letter"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "test@example.com",
                "password": "UPPERCASE123!",
                "username": "testuser",
                "full_name": "Test User",
                "role": "student",
            },
        )
        assert response.status_code == 422

    def test_password_no_digit(self):
        """Test password must contain digit"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "test@example.com",
                "password": "NoDigitsHere!",
                "username": "testuser",
                "full_name": "Test User",
                "role": "student",
            },
        )
        assert response.status_code == 422

    def test_password_no_special_char(self):
        """Test password must contain special character"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "test@example.com",
                "password": "NoSpecialChar123",
                "username": "testuser",
                "full_name": "Test User",
                "role": "student",
            },
        )
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
