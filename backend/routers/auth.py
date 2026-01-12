"""
🦁 ATHLYNX AI - Authentication Router
User Registration, Login, and Verification

@author ATHLYNX AI Corporation
@date January 12, 2026
@version 1.0
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import hashlib
import secrets
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_8rFswVRXCg0c@ep-bold-bar-aegw1i6x-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@router.post("/register")
async def register(request: Request):
    """Register a new user"""
    try:
        data = await request.json()
        
        email = data.get("email")
        password = data.get("password")
        full_name = data.get("full_name")
        phone = data.get("phone")
        role = data.get("role", "user")
        sport = data.get("sport")
        
        if not all([email, password, full_name]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (email, password_hash, full_name, phone, role, sport, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (email, password_hash, full_name, phone, role, sport, datetime.now()))
        
        user_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ New user registered: {email} (ID: {user_id})")
        
        return JSONResponse({
            "success": True,
            "message": "Registration successful! Please verify your email.",
            "user_id": user_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(request: Request):
    """Login user"""
    try:
        data = await request.json()
        
        email = data.get("email")
        password = data.get("password")
        
        if not all([email, password]):
            raise HTTPException(status_code=400, detail="Missing credentials")
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, full_name, role, verified_email, verified_phone, subscription_tier
            FROM users 
            WHERE email = %s AND password_hash = %s
        """, (email, password_hash))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate session token
        token = secrets.token_urlsafe(32)
        
        logger.info(f"✅ User logged in: {email}")
        
        return JSONResponse({
            "success": True,
            "message": "Login successful!",
            "user": dict(user),
            "token": token
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-email")
async def verify_email(request: Request):
    """Verify email with code"""
    try:
        data = await request.json()
        
        email = data.get("email")
        code = data.get("code")
        
        if not all([email, code]):
            raise HTTPException(status_code=400, detail="Missing email or code")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check verification code
        cursor.execute("""
            SELECT id, user_id FROM verification_codes
            WHERE email = %s AND code = %s AND code_type = 'email'
            AND expires_at > NOW() AND used = FALSE
            ORDER BY created_at DESC LIMIT 1
        """, (email, code))
        
        verification = cursor.fetchone()
        
        if not verification:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid or expired code")
        
        # Mark code as used
        cursor.execute("UPDATE verification_codes SET used = TRUE WHERE id = %s", (verification['id'],))
        
        # Update user verification status
        if verification['user_id']:
            cursor.execute("UPDATE users SET verified_email = TRUE WHERE id = %s", (verification['user_id'],))
        else:
            cursor.execute("UPDATE users SET verified_email = TRUE WHERE email = %s", (email,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Email verified: {email}")
        
        return JSONResponse({
            "success": True,
            "message": "Email verified successfully!"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-phone")
async def verify_phone(request: Request):
    """Verify phone with code"""
    try:
        data = await request.json()
        
        phone = data.get("phone")
        code = data.get("code")
        
        if not all([phone, code]):
            raise HTTPException(status_code=400, detail="Missing phone or code")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check verification code
        cursor.execute("""
            SELECT id, user_id FROM verification_codes
            WHERE phone = %s AND code = %s AND code_type = 'sms'
            AND expires_at > NOW() AND used = FALSE
            ORDER BY created_at DESC LIMIT 1
        """, (phone, code))
        
        verification = cursor.fetchone()
        
        if not verification:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid or expired code")
        
        # Mark code as used
        cursor.execute("UPDATE verification_codes SET used = TRUE WHERE id = %s", (verification['id'],))
        
        # Update user verification status
        if verification['user_id']:
            cursor.execute("UPDATE users SET verified_phone = TRUE WHERE id = %s", (verification['user_id'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Phone verified: {phone}")
        
        return JSONResponse({
            "success": True,
            "message": "Phone verified successfully!"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Phone verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/forgot-password")
async def forgot_password(request: Request):
    """Request password reset"""
    try:
        data = await request.json()
        email = data.get("email")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, full_name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            
            # Store reset token (would typically be in a separate table)
            # For now, we'll use verification_codes
            cursor.execute("""
                INSERT INTO verification_codes (user_id, email, code, code_type, expires_at)
                VALUES (%s, %s, %s, 'password_reset', NOW() + INTERVAL '1 hour')
            """, (user['id'], email, reset_token))
            
            conn.commit()
            
            # TODO: Send reset email via AWS SES
            logger.info(f"✅ Password reset requested for: {email}")
        
        cursor.close()
        conn.close()
        
        # Always return success to prevent email enumeration
        return JSONResponse({
            "success": True,
            "message": "If an account exists with this email, you will receive a password reset link."
        })
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user(request: Request):
    """Get current user info (requires auth token in header)"""
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        
        # In a real app, you'd validate the token and get user_id
        # For now, we'll return a placeholder
        
        return JSONResponse({
            "success": True,
            "message": "Token validation would happen here",
            "note": "Implement JWT or session-based auth for production"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
