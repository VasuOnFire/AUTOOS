"""
Authentication Middleware for AUTOOS

Provides JWT authentication, role-based authorization, subscription checks,
and rate limiting for API endpoints.
"""

import os
import time
from functools import wraps
from typing import Optional, Callable, List
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 15
REFRESH_TOKEN_EXPIRATION_DAYS = 30

# Security
security = HTTPBearer()


class AuthMiddleware:
    """JWT Authentication Middleware"""

    @staticmethod
    def create_access_token(user_id: str, email: str, role: str) -> str:
        """Create JWT access token"""
        payload = {
            "user_id": user_id,
            "email": email,
            "role": role,
            "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES),
            "iat": datetime.utcnow(),
            "type": "access",
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create JWT refresh token"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS),
            "iat": datetime.utcnow(),
            "type": "refresh",
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def get_current_user(credentials: HTTPAuthorizationCredentials) -> dict:
        """Extract current user from JWT token"""
        token = credentials.credentials
        payload = AuthMiddleware.verify_token(token)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role"),
        }

    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            # Get user data from database (simplified here)
            user_id = payload.get("user_id")

            # Create new access token
            # Note: In production, fetch user role from database
            return AuthMiddleware.create_access_token(user_id, "", "")

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )


def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract request from args/kwargs
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        if not request:
            request = kwargs.get("request")

        if not request:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Request object not found",
            )

        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract and verify token
        token = auth_header.split(" ")[1]
        user = AuthMiddleware.verify_token(token)

        # Add user to request state
        request.state.user = user

        return await func(*args, **kwargs)

    return wrapper


def require_role(allowed_roles: List[str]) -> Callable:
    """Decorator to require specific role(s)"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                request = kwargs.get("request")

            # Get user from request state (set by require_auth)
            user = getattr(request.state, "user", None)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check role
            user_role = user.get("role")
            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_subscription(allowed_tiers: Optional[List[str]] = None) -> Callable:
    """Decorator to require active subscription"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                request = kwargs.get("request")

            # Get user from request state
            user = getattr(request.state, "user", None)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check subscription status (simplified - should query database)
            # In production, fetch from database:
            # subscription = get_user_subscription(user["user_id"])
            # trial_status = get_trial_status(user["user_id"])

            # For now, assume subscription data is in request state
            subscription = getattr(request.state, "subscription", None)
            trial_status = getattr(request.state, "trial_status", None)

            # Check if user has active subscription or trial
            has_active_subscription = subscription and subscription.get("status") == "active"
            has_active_trial = trial_status and trial_status.get("is_active")

            if not has_active_subscription and not has_active_trial:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Active subscription or trial required",
                )

            # Check if trial has expired
            if has_active_trial and not has_active_subscription:
                trial_end = datetime.fromisoformat(trial_status.get("trial_end_date"))
                if datetime.now() > trial_end:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Trial has expired. Please upgrade to continue.",
                    )

                # Check trial credits
                credits_remaining = trial_status.get("credits_remaining", 0)
                if credits_remaining <= 0:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Trial credits exhausted. Please upgrade to continue.",
                    )

            # Check subscription tier if specified
            if allowed_tiers and has_active_subscription:
                user_tier = subscription.get("tier")
                if user_tier not in allowed_tiers:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"This feature requires: {', '.join(allowed_tiers)} plan",
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


class RateLimiter:
    """Rate limiting middleware"""

    def __init__(self):
        self.requests = {}  # {user_id: [(timestamp, count)]}
        self.limits = {
            "trial": {"requests_per_minute": 10, "requests_per_hour": 100},
            "student": {"requests_per_minute": 20, "requests_per_hour": 500},
            "employee": {"requests_per_minute": 50, "requests_per_hour": 2000},
            "professional": {"requests_per_minute": 100, "requests_per_hour": 10000},
            "enterprise": {"requests_per_minute": 1000, "requests_per_hour": 100000},
        }

    def check_rate_limit(self, user_id: str, tier: str) -> bool:
        """Check if user has exceeded rate limit"""
        now = time.time()
        limits = self.limits.get(tier, self.limits["trial"])

        # Initialize user request history
        if user_id not in self.requests:
            self.requests[user_id] = []

        # Clean old requests (older than 1 hour)
        self.requests[user_id] = [
            (ts, count)
            for ts, count in self.requests[user_id]
            if now - ts < 3600
        ]

        # Count requests in last minute and hour
        requests_last_minute = sum(
            count for ts, count in self.requests[user_id] if now - ts < 60
        )
        requests_last_hour = sum(count for ts, count in self.requests[user_id])

        # Check limits
        if requests_last_minute >= limits["requests_per_minute"]:
            return False
        if requests_last_hour >= limits["requests_per_hour"]:
            return False

        # Add current request
        self.requests[user_id].append((now, 1))
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


def require_rate_limit(func: Callable) -> Callable:
    """Decorator to enforce rate limiting"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract request from args/kwargs
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        if not request:
            request = kwargs.get("request")

        # Get user from request state
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        # Get user tier
        subscription = getattr(request.state, "subscription", None)
        trial_status = getattr(request.state, "trial_status", None)

        tier = "trial"
        if subscription and subscription.get("status") == "active":
            tier = subscription.get("tier", "trial")
        elif trial_status and trial_status.get("is_active"):
            tier = "trial"

        # Check rate limit
        user_id = user.get("user_id")
        if not rate_limiter.check_rate_limit(user_id, tier):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"},
            )

        return await func(*args, **kwargs)

    return wrapper


# Export all decorators and classes
__all__ = [
    "AuthMiddleware",
    "require_auth",
    "require_role",
    "require_subscription",
    "require_rate_limit",
    "RateLimiter",
    "rate_limiter",
]
