"""
🦁 ATHLYNX AI - Triple-Channel Verification Service
Email + SMS + WhatsApp Verification

@author ATHLYNX AI Corporation
@date January 12, 2026
@version 1.0
"""

import random
import string
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from typing import Optional, Tuple

from .email_service import email_service
from .sms_service import sms_service

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_8rFswVRXCg0c@ep-bold-bar-aegw1i6x-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

class VerificationService:
    """Triple-Channel Verification Service for ATHLYNX"""
    
    def __init__(self):
        self.code_length = 6
        self.code_expiry_minutes = 10
    
    def _get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    
    def _generate_code(self) -> str:
        """Generate a 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=self.code_length))
    
    def send_email_verification(self, email: str, full_name: str, user_id: Optional[int] = None) -> Tuple[bool, str]:
        """Send email verification code"""
        try:
            code = self._generate_code()
            expires_at = datetime.now() + timedelta(minutes=self.code_expiry_minutes)
            
            # Save code to database
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO verification_codes (user_id, email, code, code_type, expires_at)
                VALUES (%s, %s, %s, 'email', %s)
            """, (user_id, email, code, expires_at))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Send email
            success = email_service.send_verification_email(email, code, full_name)
            
            if success:
                logger.info(f"✅ Email verification sent to {email}")
                return True, "Verification code sent to your email"
            else:
                return False, "Failed to send verification email"
                
        except Exception as e:
            logger.error(f"❌ Email verification error: {e}")
            return False, str(e)
    
    def send_sms_verification(self, phone: str, user_id: Optional[int] = None) -> Tuple[bool, str]:
        """Send SMS verification code"""
        try:
            code = self._generate_code()
            expires_at = datetime.now() + timedelta(minutes=self.code_expiry_minutes)
            
            # Save code to database
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO verification_codes (user_id, phone, code, code_type, expires_at)
                VALUES (%s, %s, %s, 'sms', %s)
            """, (user_id, phone, code, expires_at))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Send SMS
            success = sms_service.send_verification_sms(phone, code)
            
            if success:
                logger.info(f"✅ SMS verification sent to {phone}")
                return True, "Verification code sent to your phone"
            else:
                return False, "Failed to send verification SMS"
                
        except Exception as e:
            logger.error(f"❌ SMS verification error: {e}")
            return False, str(e)
    
    def send_triple_verification(self, email: str, phone: str, full_name: str, user_id: Optional[int] = None) -> dict:
        """Send verification to all three channels"""
        results = {
            "email": {"sent": False, "message": ""},
            "sms": {"sent": False, "message": ""},
            "whatsapp": {"sent": False, "message": "Coming soon"}
        }
        
        # Send email verification
        email_success, email_msg = self.send_email_verification(email, full_name, user_id)
        results["email"]["sent"] = email_success
        results["email"]["message"] = email_msg
        
        # Send SMS verification
        sms_success, sms_msg = self.send_sms_verification(phone, user_id)
        results["sms"]["sent"] = sms_success
        results["sms"]["message"] = sms_msg
        
        # WhatsApp (future implementation)
        results["whatsapp"]["sent"] = False
        results["whatsapp"]["message"] = "WhatsApp verification coming soon"
        
        return results
    
    def verify_code(self, code: str, code_type: str, email: Optional[str] = None, phone: Optional[str] = None) -> Tuple[bool, str]:
        """Verify a code"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Build query based on type
            if code_type == 'email' and email:
                cursor.execute("""
                    SELECT id, user_id FROM verification_codes
                    WHERE email = %s AND code = %s AND code_type = 'email'
                    AND expires_at > NOW() AND used = FALSE
                    ORDER BY created_at DESC LIMIT 1
                """, (email, code))
            elif code_type == 'sms' and phone:
                cursor.execute("""
                    SELECT id, user_id FROM verification_codes
                    WHERE phone = %s AND code = %s AND code_type = 'sms'
                    AND expires_at > NOW() AND used = FALSE
                    ORDER BY created_at DESC LIMIT 1
                """, (phone, code))
            else:
                return False, "Invalid verification type"
            
            result = cursor.fetchone()
            
            if not result:
                cursor.close()
                conn.close()
                return False, "Invalid or expired code"
            
            # Mark code as used
            cursor.execute("""
                UPDATE verification_codes SET used = TRUE WHERE id = %s
            """, (result['id'],))
            
            # Update user verification status if user_id exists
            if result['user_id']:
                if code_type == 'email':
                    cursor.execute("""
                        UPDATE users SET verified_email = TRUE WHERE id = %s
                    """, (result['user_id'],))
                elif code_type == 'sms':
                    cursor.execute("""
                        UPDATE users SET verified_phone = TRUE WHERE id = %s
                    """, (result['user_id'],))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✅ {code_type.upper()} verification successful")
            return True, f"{code_type.capitalize()} verified successfully"
            
        except Exception as e:
            logger.error(f"❌ Verification error: {e}")
            return False, str(e)
    
    def check_verification_status(self, user_id: int) -> dict:
        """Check user's verification status"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT verified_email, verified_phone, verified_whatsapp
                FROM users WHERE id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return {
                    "email": result['verified_email'],
                    "phone": result['verified_phone'],
                    "whatsapp": result['verified_whatsapp'],
                    "fully_verified": all([
                        result['verified_email'],
                        result['verified_phone']
                    ])
                }
            
            return {
                "email": False,
                "phone": False,
                "whatsapp": False,
                "fully_verified": False
            }
            
        except Exception as e:
            logger.error(f"❌ Verification status check error: {e}")
            return {
                "email": False,
                "phone": False,
                "whatsapp": False,
                "fully_verified": False,
                "error": str(e)
            }

# Singleton instance
verification_service = VerificationService()
