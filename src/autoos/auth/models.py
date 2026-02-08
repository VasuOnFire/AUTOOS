"""
SQLAlchemy ORM models for authentication and payments

Database models for users, subscriptions, payments, and OAuth connections.
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class UserModel(Base):
    """User table"""

    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="student")
    subscription_tier = Column(String(50), nullable=False, default="free_trial")
    is_email_verified = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)  # Encrypted
    biometric_enabled = Column(Boolean, default=False)
    trial_start_date = Column(DateTime, nullable=True)
    trial_end_date = Column(DateTime, nullable=True)
    credits_remaining = Column(Integer, default=10)
    is_trial_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    subscriptions = relationship("SubscriptionModel", back_populates="user")
    payments = relationship("PaymentModel", back_populates="user")
    oauth_connections = relationship("OAuthConnectionModel", back_populates="user")

    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_username", "username"),
        Index("idx_user_trial_active", "is_trial_active"),
    )


class SubscriptionModel(Base):
    """Subscription table"""

    __tablename__ = "subscriptions"

    subscription_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    tier = Column(String(50), nullable=False, default="free_trial")
    status = Column(String(50), nullable=False, default="active")
    subscription_start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    subscription_end_date = Column(DateTime, nullable=True)
    payment_method = Column(String(100), nullable=True)
    billing_cycle = Column(String(20), default="monthly")
    auto_renew = Column(Boolean, default=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    workflows_limit = Column(Integer, default=10)
    agents_limit = Column(Integer, default=2)
    workflows_used = Column(Integer, default=0)

    # Relationships
    user = relationship("UserModel", back_populates="subscriptions")
    payments = relationship("PaymentModel", back_populates="subscription")

    __table_args__ = (
        Index("idx_subscription_user", "user_id"),
        Index("idx_subscription_status", "status"),
    )


class PaymentModel(Base):
    """Payment table"""

    __tablename__ = "payments"

    payment_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    subscription_id = Column(
        String(36), ForeignKey("subscriptions.subscription_id"), nullable=True
    )
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(String(50), nullable=False, default="pending")
    payment_method = Column(String(100), nullable=False)
    payment_type = Column(String(50), nullable=False, default="card")
    stripe_payment_id = Column(String(255), nullable=True)
    qr_code_payment_id = Column(String(255), nullable=True)
    qr_code_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("UserModel", back_populates="payments")
    subscription = relationship("SubscriptionModel", back_populates="payments")

    __table_args__ = (
        Index("idx_payment_user", "user_id"),
        Index("idx_payment_status", "status"),
        Index("idx_payment_created", "created_at"),
    )


class OAuthConnectionModel(Base):
    """OAuth connection table"""

    __tablename__ = "oauth_connections"

    connection_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    provider = Column(String(50), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=False)  # Encrypted
    refresh_token = Column(Text, nullable=True)  # Encrypted
    token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="oauth_connections")

    __table_args__ = (
        Index("idx_oauth_user", "user_id"),
        Index("idx_oauth_provider", "provider", "provider_user_id"),
    )
