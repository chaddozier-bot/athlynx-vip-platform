"""
🦁 ATHLYNX AI - Services Module
AWS SES, SNS, and Verification Services

@author ATHLYNX AI Corporation
@date January 12, 2026
"""

from .email_service import email_service, EmailService
from .sms_service import sms_service, SMSService
from .verification_service import verification_service, VerificationService

__all__ = [
    'email_service',
    'EmailService',
    'sms_service',
    'SMSService',
    'verification_service',
    'VerificationService'
]
