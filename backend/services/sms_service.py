"""
🦁 ATHLYNX AI - AWS SNS SMS Service
Triple-Channel Verification System

@author ATHLYNX AI Corporation
@date January 12, 2026
@version 1.0
"""

import boto3
from botocore.exceptions import ClientError
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

class SMSService:
    """AWS SNS SMS Service for ATHLYNX"""
    
    def __init__(self):
        self.client = boto3.client(
            'sns',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
    
    def send_verification_sms(self, phone_number: str, code: str) -> bool:
        """Send verification code via SMS"""
        message = f"🦁 ATHLYNX: Your verification code is {code}. Valid for 10 minutes. Dreams Do Come True 2026!"
        return self._send_sms(phone_number, message)
    
    def send_welcome_sms(self, phone_number: str, full_name: str, position: int) -> bool:
        """Send welcome SMS to new waitlist member"""
        message = f"🦁 Welcome to ATHLYNX, {full_name}! You're #{position} on our VIP waitlist. Launch: Feb 1, 2026. Dreams Do Come True!"
        return self._send_sms(phone_number, message)
    
    def send_nil_deal_sms(self, phone_number: str, brand_name: str, deal_value: float) -> bool:
        """Send NIL deal notification via SMS"""
        message = f"🎉 ATHLYNX: New NIL deal from {brand_name} - ${deal_value:,.0f}! Log in to review. Dreams Do Come True 2026!"
        return self._send_sms(phone_number, message)
    
    def send_login_alert_sms(self, phone_number: str) -> bool:
        """Send login alert SMS"""
        message = f"🦁 ATHLYNX: New login detected on your account. If this wasn't you, secure your account immediately."
        return self._send_sms(phone_number, message)
    
    def send_transfer_portal_sms(self, phone_number: str, athlete_name: str, status: str) -> bool:
        """Send transfer portal update via SMS"""
        message = f"🏈 ATHLYNX Transfer Portal: {athlete_name} status updated to {status}. Check app for details."
        return self._send_sms(phone_number, message)
    
    def _send_sms(self, phone_number: str, message: str) -> bool:
        """Internal method to send SMS via AWS SNS"""
        try:
            # Format phone number (ensure it has country code)
            if not phone_number.startswith('+'):
                phone_number = '+1' + phone_number.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            
            response = self.client.publish(
                PhoneNumber=phone_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': 'ATHLYNX'
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            
            logger.info(f"✅ SMS sent to {phone_number}: {response['MessageId']}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ SMS send error: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"❌ SMS send error: {e}")
            return False

# Singleton instance
sms_service = SMSService()
