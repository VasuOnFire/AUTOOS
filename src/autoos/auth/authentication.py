"""
AUTOOS Authentication System
Advanced multi-factor authentication with OAuth2, social login, and biometric support
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum
import jwt
import bcrypt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, validator
import pyotp
import qrcode
from io import BytesIO
import base64

# Password hashing - using argon2 to avoid bcrypt 72-byte limitation
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class UserRole(str, Enum):
    STUDENT = "student"
    EMPLOYEE = "employee"
    PROFESSIONAL = "professional"
    ADMIN = "admin"

class SubscriptionTier(str, Enum):
    FREE = "free"
    STUDENT = "student"
    EMPLOYEE = "employee"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class AuthProvider(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"
    APPLE = "apple"
    LINKEDIN = "linkedin"

class User(BaseModel):
    user_id: str
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    subscription_tier: SubscriptionTier
    auth_provider: AuthProvider
    email_verified: bool = False
    phone_verified: bool = False
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    biometric_enabled: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None
    password_hash: Optional[str] = None
    profile_picture: Optional[str] = None
    organization: Optional[str] = None
    student_id: Optional[str] = None
    employee_id: Optional[str] = None
    # Free trial fields
    is_trial_active: bool = False
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    credits_remaining: int = 0
    workflows_used: int = 0
    
    @validator('email')
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError('Invalid email address')
        return v.lower()

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    full_name: str
    role: UserRole
    auth_provider: AuthProvider = AuthProvider.EMAIL
    organization: Optional[str] = None
    student_id: Optional[str] = None
    employee_id: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        # Truncate to 72 bytes for bcrypt compatibility
        v_bytes = v.encode('utf-8')
        if len(v_bytes) > 72:
            v = v_bytes[:72].decode('utf-8', errors='ignore')
        
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain special character')
        return v

class SignInRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None
    remember_me: bool = False

class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]

class AuthenticationService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire = timedelta(hours=1)
        self.refresh_token_expire = timedelta(days=30)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        # Bcrypt has a 72-byte limit, so truncate if necessary
        password_bytes = password.encode('utf-8')[:72]
        return pwd_context.hash(password_bytes.decode('utf-8'))
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + self.access_token_expire
        
        to_encode = {
            "sub": user.user_id,
            "email": user.email,
            "role": user.role.value,
            "tier": user.subscription_tier.value,
            "exp": expire,
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + self.refresh_token_expire
        
        to_encode = {
            "sub": user.user_id,
            "exp": expire,
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def setup_mfa(self, user: User) -> MFASetupResponse:
        """Setup Multi-Factor Authentication"""
        # Generate secret
        secret = pyotp.random_base32()
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="AUTOOS"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]
        
        return MFASetupResponse(
            secret=secret,
            qr_code=f"data:image/png;base64,{qr_code_base64}",
            backup_codes=backup_codes
        )
    
    def verify_mfa_code(self, secret: str, code: str) -> bool:
        """Verify MFA code"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
    
    async def sign_up(self, request: SignUpRequest) -> User:
        """Register new user"""
        # Check if user exists
        # (Database check would go here)
        
        # Hash password
        password_hash = self.hash_password(request.password)
        
        # Determine subscription tier based on role
        # New users start with FREE tier and can activate trial
        tier = SubscriptionTier.FREE
        
        # Create user
        user = User(
            user_id=f"usr_{datetime.utcnow().timestamp()}",
            email=request.email,
            username=request.username,
            full_name=request.full_name,
            role=request.role,
            subscription_tier=tier,
            auth_provider=request.auth_provider,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            organization=request.organization,
            student_id=request.student_id,
            employee_id=request.employee_id,
            # Initialize trial fields (not activated yet)
            is_trial_active=False,
            trial_start_date=None,
            trial_end_date=None,
            credits_remaining=0,
            workflows_used=0
        )
        
        # Save to database
        # (Database save would go here)
        
        # Send verification email
        # (Email service would go here)
        
        return user
    
    async def sign_in(self, request: SignInRequest) -> Dict:
        """Authenticate user"""
        # Get user from database
        # (Database query would go here)
        user = None  # Placeholder
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not self.verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check MFA if enabled
        if user.mfa_enabled:
            if not request.mfa_code:
                return {
                    "requires_mfa": True,
                    "message": "MFA code required"
                }
            
            if not self.verify_mfa_code(user.mfa_secret, request.mfa_code):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code"
                )
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        # Create tokens
        access_token = self.create_access_token(user)
        refresh_token = self.create_refresh_token(user)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user.dict(exclude={"password_hash", "mfa_secret"})
        }
    
    async def oauth_sign_in(self, provider: AuthProvider, oauth_token: str) -> Dict:
        """Sign in with OAuth provider"""
        # Verify OAuth token with provider
        # (OAuth verification would go here)
        
        # Get or create user
        # (Database operations would go here)
        
        pass
    
    async def verify_email(self, token: str) -> bool:
        """Verify email address"""
        # Verify token and update user
        # (Database operations would go here)
        return True
    
    async def reset_password(self, email: str) -> bool:
        """Send password reset email"""
        # Generate reset token and send email
        # (Email service would go here)
        return True
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        # Verify old password and update
        # (Database operations would go here)
        return True
