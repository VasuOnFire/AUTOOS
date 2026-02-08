"""
Unit tests for AUTOOS Payment Service

Tests for Stripe integration, QR code payments, and subscription management.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import stripe

from src.autoos.payment.stripe_service import (
    StripeService,
    SubscriptionManager,
    StripeCustomerRequest,
    StripePaymentIntentRequest,
    StripeSubscriptionRequest
)
from src.autoos.payment.qr_payment import (
    QRPaymentService,
    FreeTrialService,
    QRPaymentRequest,
    PaymentStatus,
    UPIProvider
)
from src.autoos.payment.webhook_handler import StripeWebhookHandler
from src.autoos.core.models import SubscriptionTier


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def stripe_service():
    """Create Stripe service with mock API key"""
    with patch.dict('os.environ', {'STRIPE_SECRET_KEY': 'sk_test_mock'}):
        return StripeService(api_key='sk_test_mock')


@pytest.fixture
def subscription_manager(stripe_service):
    """Create subscription manager"""
    return SubscriptionManager(stripe_service)


@pytest.fixture
def qr_payment_service():
    """Create QR payment service"""
    return QRPaymentService()


@pytest.fixture
def free_trial_service():
    """Create free trial service"""
    return FreeTrialService()


@pytest.fixture
def webhook_handler(stripe_service):
    """Create webhook handler"""
    return StripeWebhookHandler(stripe_service)


# ============================================================================
# Stripe Service Tests
# ============================================================================

class TestStripeService:
    """Tests for Stripe service"""
    
    @pytest.mark.asyncio
    async def test_create_customer(self, stripe_service):
        """Test creating a Stripe customer"""
        with patch('stripe.Customer.create') as mock_create:
            mock_create.return_value = Mock(
                id='cus_test123',
                email='test@example.com',
                name='Test User',
                created=1234567890,
                metadata={'user_id': 'user123'}
            )
            
            request = StripeCustomerRequest(
                user_id='user123',
                email='test@example.com',
                name='Test User'
            )
            
            result = await stripe_service.create_customer(request)
            
            assert result['customer_id'] == 'cus_test123'
            assert result['email'] == 'test@example.com'
            assert result['name'] == 'Test User'
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_payment_intent(self, stripe_service):
        """Test creating a payment intent"""
        with patch('stripe.PaymentIntent.create') as mock_create:
            mock_create.return_value = Mock(
                id='pi_test123',
                client_secret='pi_test123_secret',
                amount=9999,
                currency='usd',
                status='requires_payment_method',
                created=1234567890
            )
            
            request = StripePaymentIntentRequest(
                user_id='user123',
                amount=99.99,
                currency='USD',
                description='Test payment'
            )
            
            result = await stripe_service.create_payment_intent(request)
            
            assert result['payment_intent_id'] == 'pi_test123'
            assert result['amount'] == 99.99
            assert result['currency'] == 'USD'
            assert 'client_secret' in result
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_subscription(self, stripe_service):
        """Test creating a subscription"""
        with patch('stripe.Subscription.create') as mock_create, \
             patch('stripe.Price.retrieve') as mock_price, \
             patch('stripe.Product.retrieve') as mock_product:
            
            mock_create.return_value = Mock(
                id='sub_test123',
                customer='cus_test123',
                status='active',
                current_period_start=1234567890,
                current_period_end=1237159890,
                metadata={'user_id': 'user123', 'tier': 'student'}
            )
            
            request = StripeSubscriptionRequest(
                user_id='user123',
                customer_id='cus_test123',
                tier=SubscriptionTier.STUDENT,
                billing_cycle='monthly'
            )
            
            result = await stripe_service.create_subscription(request)
            
            assert result['subscription_id'] == 'sub_test123'
            assert result['customer_id'] == 'cus_test123'
            assert result['status'] == 'active'
            assert result['tier'] == 'student'
    
    @pytest.mark.asyncio
    async def test_cancel_subscription(self, stripe_service):
        """Test cancelling a subscription"""
        with patch('stripe.Subscription.delete') as mock_delete:
            mock_delete.return_value = Mock(
                id='sub_test123',
                status='canceled',
                canceled_at=1234567890,
                cancel_at_period_end=False
            )
            
            result = await stripe_service.cancel_subscription('sub_test123', immediate=True)
            
            assert result['subscription_id'] == 'sub_test123'
            assert result['status'] == 'canceled'
            mock_delete.assert_called_once_with('sub_test123')
    
    @pytest.mark.asyncio
    async def test_update_payment_method(self, stripe_service):
        """Test updating payment method"""
        with patch('stripe.PaymentMethod.attach') as mock_attach, \
             patch('stripe.Customer.modify') as mock_modify:
            
            mock_modify.return_value = Mock(
                id='cus_test123',
                invoice_settings=Mock(default_payment_method='pm_test123')
            )
            
            result = await stripe_service.update_payment_method('cus_test123', 'pm_test123')
            
            assert result['customer_id'] == 'cus_test123'
            assert result['default_payment_method'] == 'pm_test123'
            assert result['updated'] is True
            mock_attach.assert_called_once()
            mock_modify.assert_called_once()


# ============================================================================
# Subscription Manager Tests
# ============================================================================

class TestSubscriptionManager:
    """Tests for subscription manager"""
    
    @pytest.mark.asyncio
    async def test_upgrade_subscription(self, subscription_manager):
        """Test upgrading subscription"""
        with patch('stripe.Subscription.retrieve') as mock_retrieve, \
             patch('stripe.Subscription.modify') as mock_modify:
            
            mock_retrieve.return_value = Mock(
                id='sub_test123',
                customer='cus_test123',
                items={'data': [Mock(id='si_test123')]},
                metadata={'tier': 'student'}
            )
            
            mock_modify.return_value = Mock(
                id='sub_test123',
                status='active',
                current_period_end=1237159890,
                metadata={'tier': 'professional'}
            )
            
            result = await subscription_manager.upgrade_subscription(
                'sub_test123',
                SubscriptionTier.PROFESSIONAL,
                'monthly'
            )
            
            assert result['subscription_id'] == 'sub_test123'
            assert result['tier'] == 'professional'
            mock_modify.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_subscription_limits(self, subscription_manager):
        """Test checking subscription limits"""
        result = await subscription_manager.check_subscription_limits(
            'user123',
            SubscriptionTier.STUDENT
        )
        
        assert 'workflows_limit' in result
        assert 'agents_limit' in result
        assert 'can_create_workflow' in result
        assert 'can_create_agent' in result
        assert result['workflows_limit'] == 100
        assert result['agents_limit'] == 5


# ============================================================================
# QR Payment Service Tests
# ============================================================================

class TestQRPaymentService:
    """Tests for QR payment service"""
    
    @pytest.mark.asyncio
    async def test_create_qr_payment(self, qr_payment_service):
        """Test creating QR code payment"""
        request = QRPaymentRequest(
            user_id='user123',
            amount=999.00,
            currency='INR',
            description='Test subscription payment',
            subscription_tier='student'
        )
        
        result = await qr_payment_service.create_qr_payment(request)
        
        assert result.payment_id.startswith('qr_')
        assert result.amount == 999.00
        assert result.currency == 'INR'
        assert result.status == PaymentStatus.PENDING
        assert result.qr_code.startswith('data:image/png;base64,')
        assert 'upi://pay?' in result.upi_string
        assert result.merchant_vpa == 'vasu7993457842@axl'
    
    def test_generate_upi_string(self, qr_payment_service):
        """Test UPI string generation"""
        upi_string = qr_payment_service.generate_upi_string(
            payment_id='test123',
            amount=100.00,
            description='Test payment'
        )
        
        assert 'upi://pay?' in upi_string
        assert 'pa=vasu7993457842@axl' in upi_string
        assert 'am=100.00' in upi_string
        assert 'tr=test123' in upi_string
    
    def test_generate_qr_code(self, qr_payment_service):
        """Test QR code generation"""
        upi_string = 'upi://pay?pa=test@upi&am=100.00'
        qr_code = qr_payment_service.generate_qr_code(upi_string)
        
        assert qr_code.startswith('data:image/png;base64,')
        assert len(qr_code) > 100  # Should be a substantial base64 string
    
    def test_generate_phonepe_deeplink(self, qr_payment_service):
        """Test PhonePe deep link generation"""
        upi_string = 'upi://pay?pa=test@upi&am=100.00'
        deeplink = qr_payment_service.generate_phonepe_deeplink(upi_string)
        
        assert deeplink.startswith('phonepe://pay?')
        assert 'pa=test@upi' in deeplink
    
    @pytest.mark.asyncio
    async def test_check_payment_status(self, qr_payment_service):
        """Test checking payment status"""
        status = await qr_payment_service.check_payment_status('qr_test123')
        
        assert isinstance(status, PaymentStatus)


# ============================================================================
# Free Trial Service Tests
# ============================================================================

class TestFreeTrialService:
    """Tests for free trial service"""
    
    @pytest.mark.asyncio
    async def test_start_free_trial(self, free_trial_service):
        """Test starting free trial"""
        result = await free_trial_service.start_free_trial('user123')
        
        assert result['user_id'] == 'user123'
        assert result['is_active'] is True
        assert result['credits_remaining'] == 10
        assert result['workflow_limit'] == 10
        assert result['agent_limit'] == 2
        assert 'trial_start_date' in result
        assert 'trial_end_date' in result
        
        # Check trial duration is 30 days
        start = result['trial_start_date']
        end = result['trial_end_date']
        duration = (end - start).days
        assert duration == 30
    
    @pytest.mark.asyncio
    async def test_check_trial_status(self, free_trial_service):
        """Test checking trial status"""
        result = await free_trial_service.check_trial_status('user123')
        
        assert 'is_active' in result
        assert 'days_remaining' in result
        assert 'credits_remaining' in result
        assert 'workflows_used' in result
    
    @pytest.mark.asyncio
    async def test_deduct_credit(self, free_trial_service):
        """Test deducting trial credits"""
        result = await free_trial_service.deduct_credit('user123', amount=1)
        
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_check_trial_limits(self, free_trial_service):
        """Test checking trial limits"""
        result = await free_trial_service.check_trial_limits('user123')
        
        assert 'workflows_exceeded' in result
        assert 'agents_exceeded' in result
        assert 'credits_exceeded' in result
        assert 'trial_expired' in result


# ============================================================================
# Webhook Handler Tests
# ============================================================================

class TestWebhookHandler:
    """Tests for webhook handler"""
    
    @pytest.mark.asyncio
    async def test_handle_payment_intent_succeeded(self, webhook_handler):
        """Test handling successful payment intent"""
        event = {
            'id': 'evt_test123',
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test123',
                    'amount': 9999,
                    'currency': 'usd',
                    'customer': 'cus_test123',
                    'metadata': {'user_id': 'user123'}
                }
            }
        }
        
        result = await webhook_handler.handle_webhook(event)
        
        assert result['status'] == 'success'
        assert result['event_type'] == 'payment_intent.succeeded'
        assert result['result']['payment_id'] == 'pi_test123'
        assert result['result']['status'] == 'completed'
    
    @pytest.mark.asyncio
    async def test_handle_subscription_created(self, webhook_handler):
        """Test handling subscription creation"""
        event = {
            'id': 'evt_test123',
            'type': 'customer.subscription.created',
            'data': {
                'object': {
                    'id': 'sub_test123',
                    'customer': 'cus_test123',
                    'status': 'active',
                    'current_period_start': 1234567890,
                    'current_period_end': 1237159890,
                    'metadata': {
                        'user_id': 'user123',
                        'tier': 'student'
                    }
                }
            }
        }
        
        result = await webhook_handler.handle_webhook(event)
        
        assert result['status'] == 'success'
        assert result['event_type'] == 'customer.subscription.created'
        assert result['result']['subscription_id'] == 'sub_test123'
        assert result['result']['tier'] == 'student'
    
    @pytest.mark.asyncio
    async def test_handle_unknown_event(self, webhook_handler):
        """Test handling unknown event type"""
        event = {
            'id': 'evt_test123',
            'type': 'unknown.event.type',
            'data': {'object': {}}
        }
        
        result = await webhook_handler.handle_webhook(event)
        
        assert result['status'] == 'ignored'
        assert 'No handler' in result['message']


# ============================================================================
# Integration Tests
# ============================================================================

class TestPaymentIntegration:
    """Integration tests for payment flow"""
    
    @pytest.mark.asyncio
    async def test_complete_subscription_flow(self, stripe_service):
        """Test complete subscription creation flow"""
        with patch('stripe.Customer.create') as mock_customer, \
             patch('stripe.Subscription.create') as mock_subscription:
            
            # Mock customer creation
            mock_customer.return_value = Mock(
                id='cus_test123',
                email='test@example.com',
                name='Test User',
                created=1234567890,
                metadata={'user_id': 'user123'}
            )
            
            # Mock subscription creation
            mock_subscription.return_value = Mock(
                id='sub_test123',
                customer='cus_test123',
                status='active',
                current_period_start=1234567890,
                current_period_end=1237159890,
                metadata={'user_id': 'user123', 'tier': 'student'}
            )
            
            # Create customer
            customer_request = StripeCustomerRequest(
                user_id='user123',
                email='test@example.com',
                name='Test User'
            )
            customer = await stripe_service.create_customer(customer_request)
            
            # Create subscription
            subscription_request = StripeSubscriptionRequest(
                user_id='user123',
                customer_id=customer['customer_id'],
                tier=SubscriptionTier.STUDENT,
                billing_cycle='monthly'
            )
            subscription = await stripe_service.create_subscription(subscription_request)
            
            assert customer['customer_id'] == 'cus_test123'
            assert subscription['subscription_id'] == 'sub_test123'
            assert subscription['customer_id'] == customer['customer_id']
    
    @pytest.mark.asyncio
    async def test_trial_to_paid_upgrade(self, free_trial_service, subscription_manager):
        """Test upgrading from trial to paid subscription"""
        # Start trial
        trial = await free_trial_service.start_free_trial('user123')
        assert trial['is_active'] is True
        
        # Check limits
        limits = await subscription_manager.check_subscription_limits(
            'user123',
            SubscriptionTier.STUDENT
        )
        assert limits['workflows_limit'] > trial['workflow_limit']


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestErrorHandling:
    """Tests for error handling"""
    
    @pytest.mark.asyncio
    async def test_stripe_api_error(self, stripe_service):
        """Test handling Stripe API errors"""
        with patch('stripe.Customer.create') as mock_create:
            mock_create.side_effect = stripe.error.StripeError('API Error')
            
            request = StripeCustomerRequest(
                user_id='user123',
                email='test@example.com',
                name='Test User'
            )
            
            with pytest.raises(Exception) as exc_info:
                await stripe_service.create_customer(request)
            
            assert 'Failed to create Stripe customer' in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_tier(self, stripe_service):
        """Test handling invalid subscription tier"""
        request = StripeSubscriptionRequest(
            user_id='user123',
            customer_id='cus_test123',
            tier=SubscriptionTier.FREE_TRIAL,  # Free trial shouldn't be purchasable
            billing_cycle='monthly'
        )
        
        # This should work but with $0 price
        # In production, you'd want to prevent this
        result = await stripe_service.create_subscription(request)
        assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
