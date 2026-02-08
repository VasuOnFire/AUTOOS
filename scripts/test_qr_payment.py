#!/usr/bin/env python3
"""
Test script for QR code payment generation
Demonstrates UPI QR code generation with vasu7993457842@axl
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.autoos.payment.qr_payment import (
    QRPaymentService,
    QRPaymentRequest,
    UPIProvider
)
import asyncio


async def test_qr_generation():
    """Test QR code generation with default UPI ID"""
    
    print("=" * 60)
    print("AUTOOS QR Payment Test")
    print("=" * 60)
    print()
    
    # Initialize service with default UPI ID (vasu7993457842@axl)
    service = QRPaymentService()
    
    print(f"Merchant VPA: {service.merchant_vpa}")
    print(f"Merchant Name: {service.merchant_name}")
    print()
    
    # Create test payment request
    request = QRPaymentRequest(
        user_id="test_user_123",
        amount=99.99,
        currency="INR",
        description="AUTOOS Professional Subscription",
        subscription_tier="professional",
        upi_provider=UPIProvider.ANY
    )
    
    print("Creating QR payment...")
    print(f"Amount: ₹{request.amount}")
    print(f"Description: {request.description}")
    print()
    
    # Generate QR code
    response = await service.create_qr_payment(request)
    
    print("✅ QR Payment Created Successfully!")
    print()
    print(f"Payment ID: {response.payment_id}")
    print(f"Status: {response.status}")
    print(f"Expires At: {response.expires_at}")
    print()
    print("UPI String:")
    print(response.upi_string)
    print()
    print("QR Code (Base64):")
    print(response.qr_code[:100] + "...")
    print()
    
    # Generate deep links for different UPI apps
    print("Deep Links for UPI Apps:")
    print("-" * 60)
    
    phonepe_link = service.generate_phonepe_deeplink(response.upi_string)
    print(f"PhonePe: {phonepe_link}")
    
    googlepay_link = service.generate_googlepay_deeplink(response.upi_string)
    print(f"Google Pay: {googlepay_link}")
    
    paytm_link = service.generate_paytm_deeplink(response.upi_string)
    print(f"Paytm: {paytm_link}")
    print()
    
    # Save QR code to file
    qr_data = response.qr_code.split(',')[1]  # Remove data:image/png;base64, prefix
    
    import base64
    with open('test_qr_code.png', 'wb') as f:
        f.write(base64.b64decode(qr_data))
    
    print("✅ QR code saved to: test_qr_code.png")
    print()
    print("You can scan this QR code with any UPI app to make payment!")
    print("=" * 60)


async def test_different_amounts():
    """Test QR generation for different subscription tiers"""
    
    print()
    print("=" * 60)
    print("Testing Different Subscription Tiers")
    print("=" * 60)
    print()
    
    service = QRPaymentService()
    
    tiers = [
        ("Student", 9.99),
        ("Employee", 29.99),
        ("Professional", 99.99),
        ("Enterprise", 499.99)
    ]
    
    for tier_name, amount in tiers:
        request = QRPaymentRequest(
            user_id="test_user",
            amount=amount,
            currency="INR",
            description=f"AUTOOS {tier_name} Subscription",
            subscription_tier=tier_name.lower()
        )
        
        response = await service.create_qr_payment(request)
        
        print(f"✅ {tier_name} Tier - ₹{amount}")
        print(f"   Payment ID: {response.payment_id}")
        print(f"   UPI: {response.upi_string[:80]}...")
        print()


async def test_custom_upi():
    """Test with custom UPI ID"""
    
    print()
    print("=" * 60)
    print("Testing Custom UPI ID")
    print("=" * 60)
    print()
    
    # You can override the default UPI ID if needed
    custom_service = QRPaymentService(
        merchant_vpa="custom@paytm",
        merchant_name="Custom Merchant"
    )
    
    print(f"Custom Merchant VPA: {custom_service.merchant_vpa}")
    print(f"Custom Merchant Name: {custom_service.merchant_name}")
    print()
    
    request = QRPaymentRequest(
        user_id="test_user",
        amount=50.00,
        currency="INR",
        description="Test Payment"
    )
    
    response = await custom_service.create_qr_payment(request)
    print(f"✅ Payment created with custom UPI")
    print(f"   UPI String: {response.upi_string}")
    print()


async def main():
    """Run all tests"""
    try:
        await test_qr_generation()
        await test_different_amounts()
        await test_custom_upi()
        
        print()
        print("=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
