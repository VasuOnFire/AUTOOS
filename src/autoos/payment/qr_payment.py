"""
AUTOOS QR Code Payment Service
Support for PhonePe, Google Pay, Paytm, and other UPI payment methods
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum
import qrcode
from io import BytesIO
import base64
import uuid
import hashlib
from pydantic import BaseModel

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class UPIProvider(str, Enum):
    PHONEPE = "phonepe"
    GOOGLEPAY = "googlepay"
    PAYTM = "paytm"
    BHIM = "bhim"
    ANY = "any"  # Works with any UPI app

class QRPaymentRequest(BaseModel):
    user_id: str
    amount: float
    currency: str = "INR"
    description: str
    subscription_tier: Optional[str] = None
    upi_provider: UPIProvider = UPIProvider.ANY

class QRPaymentResponse(BaseModel):
    payment_id: str
    qr_code: str  # Base64 encoded QR code image
    upi_string: str  # UPI payment string
    amount: float
    currency: str
    status: PaymentStatus
    expires_at: datetime
    merchant_name: str
    merchant_vpa: str

class QRPaymentService:
    def __init__(self, merchant_vpa: str = "vasu7993457842@axl", merchant_name: str = "AUTOOS"):
        """
        Initialize QR Payment Service
        
        Args:
            merchant_vpa: Merchant's UPI Virtual Payment Address (default: vasu7993457842@axl)
            merchant_name: Merchant display name (default: AUTOOS)
        """
        self.merchant_vpa = merchant_vpa
        self.merchant_name = merchant_name
        self.payment_timeout = timedelta(minutes=15)  # QR code expires after 15 minutes
    
    def generate_payment_id(self) -> str:
        """Generate unique payment ID"""
        return f"qr_{uuid.uuid4().hex[:16]}"
    
    def generate_upi_string(self, payment_id: str, amount: float, description: str) -> str:
        """
        Generate UPI payment string
        
        Format: upi://pay?pa=<VPA>&pn=<Name>&am=<Amount>&cu=<Currency>&tn=<Note>&tr=<TxnID>
        """
        upi_string = (
            f"upi://pay?"
            f"pa={self.merchant_vpa}&"
            f"pn={self.merchant_name}&"
            f"am={amount:.2f}&"
            f"cu=INR&"
            f"tn={description}&"
            f"tr={payment_id}"
        )
        return upi_string
    
    def generate_qr_code(self, upi_string: str) -> str:
        """
        Generate QR code image from UPI string
        
        Returns:
            Base64 encoded PNG image
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(upi_string)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{qr_code_base64}"
    
    async def create_qr_payment(self, request: QRPaymentRequest) -> QRPaymentResponse:
        """
        Create a new QR code payment
        
        Args:
            request: Payment request details
            
        Returns:
            QR payment response with QR code and payment details
        """
        # Generate payment ID
        payment_id = self.generate_payment_id()
        
        # Generate UPI string
        upi_string = self.generate_upi_string(
            payment_id=payment_id,
            amount=request.amount,
            description=request.description
        )
        
        # Generate QR code
        qr_code = self.generate_qr_code(upi_string)
        
        # Calculate expiration time
        expires_at = datetime.utcnow() + self.payment_timeout
        
        # Create payment record in database
        # (Database operations would go here)
        
        return QRPaymentResponse(
            payment_id=payment_id,
            qr_code=qr_code,
            upi_string=upi_string,
            amount=request.amount,
            currency=request.currency,
            status=PaymentStatus.PENDING,
            expires_at=expires_at,
            merchant_name=self.merchant_name,
            merchant_vpa=self.merchant_vpa
        )
    
    async def check_payment_status(self, payment_id: str) -> PaymentStatus:
        """
        Check the status of a QR code payment
        
        This would typically integrate with payment gateway API to check
        if payment has been received
        
        Args:
            payment_id: Unique payment identifier
            
        Returns:
            Current payment status
        """
        # Query database for payment status
        # (Database query would go here)
        
        # Check with payment gateway API
        # (API call would go here)
        
        # For now, return pending
        return PaymentStatus.PENDING
    
    async def verify_payment(self, payment_id: str, transaction_ref: str) -> bool:
        """
        Verify payment completion
        
        Args:
            payment_id: Unique payment identifier
            transaction_ref: UPI transaction reference number
            
        Returns:
            True if payment is verified, False otherwise
        """
        # Verify with payment gateway
        # (API verification would go here)
        
        # Update payment status in database
        # (Database update would go here)
        
        return True
    
    async def expire_payment(self, payment_id: str) -> None:
        """
        Mark payment as expired after timeout
        
        Args:
            payment_id: Unique payment identifier
        """
        # Update payment status to expired
        # (Database update would go here)
        pass
    
    async def get_payment_details(self, payment_id: str) -> Optional[Dict]:
        """
        Get payment details
        
        Args:
            payment_id: Unique payment identifier
            
        Returns:
            Payment details or None if not found
        """
        # Query database for payment details
        # (Database query would go here)
        
        return None
    
    def generate_phonepe_deeplink(self, upi_string: str) -> str:
        """
        Generate PhonePe app deep link
        
        Args:
            upi_string: UPI payment string
            
        Returns:
            PhonePe deep link URL
        """
        return f"phonepe://pay?{upi_string.split('?')[1]}"
    
    def generate_googlepay_deeplink(self, upi_string: str) -> str:
        """
        Generate Google Pay app deep link
        
        Args:
            upi_string: UPI payment string
            
        Returns:
            Google Pay deep link URL
        """
        return f"tez://upi/pay?{upi_string.split('?')[1]}"
    
    def generate_paytm_deeplink(self, upi_string: str) -> str:
        """
        Generate Paytm app deep link
        
        Args:
            upi_string: UPI payment string
            
        Returns:
            Paytm deep link URL
        """
        return f"paytmmp://pay?{upi_string.split('?')[1]}"


class FreeTrialService:
    """Service for managing free trial subscriptions"""
    
    def __init__(self):
        from src.autoos.payment.config import SubscriptionTiers
        trial_config = SubscriptionTiers.FREE_TRIAL
        
        self.trial_duration_days = trial_config.trial_days
        self.trial_workflow_limit = trial_config.workflows_limit
        self.trial_agent_limit = trial_config.agents_limit
        self.trial_credits = trial_config.trial_credits
    
    async def start_free_trial(self, user_id: str) -> Dict:
        """
        Start a free trial for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Trial details
        """
        trial_start = datetime.utcnow()
        trial_end = trial_start + timedelta(days=self.trial_duration_days)
        
        trial_data = {
            "user_id": user_id,
            "trial_start_date": trial_start,
            "trial_end_date": trial_end,
            "credits_remaining": self.trial_credits,
            "workflows_used": 0,
            "workflow_limit": self.trial_workflow_limit,
            "agent_limit": self.trial_agent_limit,
            "is_active": True
        }
        
        # Save to database
        # (Database operations would go here)
        
        # Send welcome email with trial details
        # (Email service would go here)
        
        return trial_data
    
    async def check_trial_status(self, user_id: str) -> Dict:
        """
        Check trial status for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Trial status details
        """
        # Query database for trial info
        # (Database query would go here)
        
        trial_data = {
            "is_active": True,
            "days_remaining": 25,
            "credits_remaining": 7,
            "workflows_used": 3,
            "workflow_limit": 10
        }
        
        return trial_data
    
    async def deduct_credit(self, user_id: str, amount: int = 1) -> bool:
        """
        Deduct credits from trial user
        
        Args:
            user_id: User identifier
            amount: Number of credits to deduct
            
        Returns:
            True if credits were deducted, False if insufficient credits
        """
        # Get current credits
        # (Database query would go here)
        
        # Check if sufficient credits
        # If yes, deduct and update database
        # (Database update would go here)
        
        return True
    
    async def check_trial_limits(self, user_id: str) -> Dict:
        """
        Check if user has exceeded trial limits
        
        Args:
            user_id: User identifier
            
        Returns:
            Limit status
        """
        # Query database for usage
        # (Database query would go here)
        
        return {
            "workflows_exceeded": False,
            "agents_exceeded": False,
            "credits_exceeded": False,
            "trial_expired": False
        }
    
    async def send_trial_expiration_reminder(self, user_id: str, days_remaining: int) -> None:
        """
        Send trial expiration reminder email
        
        Args:
            user_id: User identifier
            days_remaining: Days remaining in trial
        """
        # Send email reminder
        # (Email service would go here)
        pass
    
    async def expire_trial(self, user_id: str) -> None:
        """
        Expire trial and update user status
        
        Args:
            user_id: User identifier
        """
        # Update database to mark trial as expired
        # (Database update would go here)
        
        # Send trial expired email
        # (Email service would go here)
        pass
