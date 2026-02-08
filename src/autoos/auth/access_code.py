"""
Access Code System for AUTOOS

Users receive a unique access code after payment to access the app.
When subscription expires, they need to pay again for a new code.
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict
from dataclasses import dataclass
from enum import Enum


class AccessCodeStatus(str, Enum):
    """Access code status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    USED = "used"


@dataclass
class AccessCode:
    """Access code data"""
    code: str
    user_id: str
    subscription_tier: str
    created_at: datetime
    expires_at: datetime
    status: AccessCodeStatus
    payment_id: str
    usage_count: int = 0
    last_used_at: Optional[datetime] = None


class AccessCodeGenerator:
    """Generate and manage access codes"""
    
    def __init__(self):
        self.code_length = 16
        self.code_prefix = "AUTOOS"
        
    def generate_code(self) -> str:
        """
        Generate a unique access code
        
        Format: AUTOOS-XXXX-XXXX-XXXX-XXXX
        Example: AUTOOS-A7B9-C2D4-E6F8-G1H3
        """
        # Generate random alphanumeric string
        chars = string.ascii_uppercase + string.digits
        code_parts = []
        
        for _ in range(4):
            part = ''.join(secrets.choice(chars) for _ in range(4))
            code_parts.append(part)
        
        code = f"{self.code_prefix}-{'-'.join(code_parts)}"
        return code
    
    def create_access_code(
        self,
        user_id: str,
        subscription_tier: str,
        payment_id: str,
        duration_days: int = 30
    ) -> AccessCode:
        """
        Create a new access code after successful payment
        
        Args:
            user_id: User identifier
            subscription_tier: Subscription tier (student, employee, professional)
            payment_id: Payment transaction ID
            duration_days: Subscription duration in days
            
        Returns:
            AccessCode object
        """
        code = self.generate_code()
        now = datetime.utcnow()
        expires_at = now + timedelta(days=duration_days)
        
        access_code = AccessCode(
            code=code,
            user_id=user_id,
            subscription_tier=subscription_tier,
            created_at=now,
            expires_at=expires_at,
            status=AccessCodeStatus.ACTIVE,
            payment_id=payment_id
        )
        
        # Save to database
        # (Database operation would go here)
        
        return access_code
    
    def verify_access_code(self, code: str) -> Dict:
        """
        Verify if access code is valid
        
        Args:
            code: Access code to verify
            
        Returns:
            Verification result with status and details
        """
        # Query database for access code
        # (Database query would go here)
        
        # For now, return mock data
        access_code = None  # Get from database
        
        if not access_code:
            return {
                "valid": False,
                "reason": "Invalid access code",
                "status": "invalid"
            }
        
        # Check if expired
        if access_code.expires_at < datetime.utcnow():
            return {
                "valid": False,
                "reason": "Access code has expired",
                "status": "expired",
                "expired_at": access_code.expires_at,
                "subscription_tier": access_code.subscription_tier
            }
        
        # Check if revoked
        if access_code.status == AccessCodeStatus.REVOKED:
            return {
                "valid": False,
                "reason": "Access code has been revoked",
                "status": "revoked"
            }
        
        # Valid code
        return {
            "valid": True,
            "user_id": access_code.user_id,
            "subscription_tier": access_code.subscription_tier,
            "expires_at": access_code.expires_at,
            "days_remaining": (access_code.expires_at - datetime.utcnow()).days,
            "status": "active"
        }
    
    def use_access_code(self, code: str) -> bool:
        """
        Mark access code as used and update usage count
        
        Args:
            code: Access code
            
        Returns:
            True if successful, False otherwise
        """
        # Verify code first
        verification = self.verify_access_code(code)
        
        if not verification["valid"]:
            return False
        
        # Update usage count and last used timestamp
        # (Database update would go here)
        
        return True
    
    def revoke_access_code(self, code: str, reason: str = "Manual revocation") -> bool:
        """
        Revoke an access code
        
        Args:
            code: Access code to revoke
            reason: Reason for revocation
            
        Returns:
            True if successful, False otherwise
        """
        # Update database to mark code as revoked
        # (Database update would go here)
        
        return True
    
    def get_user_active_code(self, user_id: str) -> Optional[AccessCode]:
        """
        Get user's currently active access code
        
        Args:
            user_id: User identifier
            
        Returns:
            Active AccessCode or None
        """
        # Query database for active code
        # (Database query would go here)
        
        return None
    
    def check_expiration_and_notify(self, user_id: str) -> Dict:
        """
        Check if user's access code is expiring soon and send notifications
        
        Args:
            user_id: User identifier
            
        Returns:
            Expiration status
        """
        active_code = self.get_user_active_code(user_id)
        
        if not active_code:
            return {
                "has_active_code": False,
                "needs_renewal": True
            }
        
        days_remaining = (active_code.expires_at - datetime.utcnow()).days
        
        # Send notifications at 7, 3, and 1 day before expiration
        if days_remaining in [7, 3, 1]:
            # Send expiration reminder email
            # (Email service would go here)
            pass
        
        return {
            "has_active_code": True,
            "days_remaining": days_remaining,
            "expires_at": active_code.expires_at,
            "needs_renewal": days_remaining <= 3,
            "code": active_code.code
        }


class SubscriptionRenewalService:
    """Handle subscription renewals and access code regeneration"""
    
    def __init__(self):
        self.code_generator = AccessCodeGenerator()
    
    def renew_subscription(
        self,
        user_id: str,
        subscription_tier: str,
        payment_id: str
    ) -> Dict:
        """
        Renew subscription after payment and generate new access code
        
        Args:
            user_id: User identifier
            subscription_tier: Subscription tier
            payment_id: New payment transaction ID
            
        Returns:
            Renewal details with new access code
        """
        # Get duration based on tier
        duration_map = {
            "student": 30,
            "employee": 30,
            "professional": 30,
            "enterprise": 365
        }
        duration_days = duration_map.get(subscription_tier, 30)
        
        # Revoke old access code if exists
        old_code = self.code_generator.get_user_active_code(user_id)
        if old_code:
            self.code_generator.revoke_access_code(
                old_code.code,
                reason="Subscription renewed"
            )
        
        # Generate new access code
        new_code = self.code_generator.create_access_code(
            user_id=user_id,
            subscription_tier=subscription_tier,
            payment_id=payment_id,
            duration_days=duration_days
        )
        
        # Send email with new access code
        # (Email service would go here)
        
        return {
            "success": True,
            "access_code": new_code.code,
            "expires_at": new_code.expires_at,
            "subscription_tier": subscription_tier,
            "duration_days": duration_days
        }
    
    def handle_expired_subscription(self, user_id: str) -> Dict:
        """
        Handle expired subscription
        
        Args:
            user_id: User identifier
            
        Returns:
            Expiration handling result
        """
        # Mark access code as expired
        active_code = self.code_generator.get_user_active_code(user_id)
        
        if active_code:
            # Update status to expired
            # (Database update would go here)
            
            # Send expiration email with renewal link
            # (Email service would go here)
            pass
        
        return {
            "subscription_expired": True,
            "needs_payment": True,
            "renewal_url": "/payments/renew"
        }
    
    def get_renewal_pricing(self, subscription_tier: str) -> Dict:
        """
        Get renewal pricing for subscription tier
        
        Args:
            subscription_tier: Subscription tier
            
        Returns:
            Pricing information
        """
        pricing = {
            "student": {
                "monthly_inr": 799,
                "monthly_usd": 9.99,
                "duration_days": 30
            },
            "employee": {
                "monthly_inr": 2399,
                "monthly_usd": 29.99,
                "duration_days": 30
            },
            "professional": {
                "monthly_inr": 7999,
                "monthly_usd": 99.99,
                "duration_days": 30
            },
            "enterprise": {
                "monthly_inr": 0,  # Custom
                "monthly_usd": 0,  # Custom
                "duration_days": 365
            }
        }
        
        return pricing.get(subscription_tier, pricing["student"])


# Example usage
if __name__ == "__main__":
    # Initialize services
    code_gen = AccessCodeGenerator()
    renewal_service = SubscriptionRenewalService()
    
    # Scenario 1: User pays for subscription
    print("=" * 60)
    print("Scenario 1: User Pays for Subscription")
    print("=" * 60)
    
    access_code = code_gen.create_access_code(
        user_id="user_123",
        subscription_tier="professional",
        payment_id="pay_abc123",
        duration_days=30
    )
    
    print(f"✅ Payment Successful!")
    print(f"Access Code: {access_code.code}")
    print(f"Tier: {access_code.subscription_tier}")
    print(f"Expires: {access_code.expires_at}")
    print(f"Duration: 30 days")
    print()
    
    # Scenario 2: User enters access code to use app
    print("=" * 60)
    print("Scenario 2: User Enters Access Code")
    print("=" * 60)
    
    verification = code_gen.verify_access_code(access_code.code)
    
    if verification["valid"]:
        print(f"✅ Access Code Valid!")
        print(f"User ID: {verification['user_id']}")
        print(f"Tier: {verification['subscription_tier']}")
        print(f"Days Remaining: {verification['days_remaining']}")
        print(f"Status: {verification['status']}")
    else:
        print(f"❌ Access Code Invalid: {verification['reason']}")
    print()
    
    # Scenario 3: Subscription expires
    print("=" * 60)
    print("Scenario 3: Subscription Expires")
    print("=" * 60)
    
    expiration_result = renewal_service.handle_expired_subscription("user_123")
    
    print(f"⚠️ Subscription Expired!")
    print(f"Needs Payment: {expiration_result['needs_payment']}")
    print(f"Renewal URL: {expiration_result['renewal_url']}")
    print()
    
    # Scenario 4: User pays again for renewal
    print("=" * 60)
    print("Scenario 4: User Pays for Renewal")
    print("=" * 60)
    
    renewal_result = renewal_service.renew_subscription(
        user_id="user_123",
        subscription_tier="professional",
        payment_id="pay_xyz789"
    )
    
    print(f"✅ Subscription Renewed!")
    print(f"New Access Code: {renewal_result['access_code']}")
    print(f"Expires: {renewal_result['expires_at']}")
    print(f"Duration: {renewal_result['duration_days']} days")
    print()
    
    print("=" * 60)
    print("Process Complete - Cycle Repeats!")
    print("=" * 60)
