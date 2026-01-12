"""
🦁 ATHLYNX AI - AWS SES Email Service
Triple-Channel Verification System

@author ATHLYNX AI Corporation
@date January 12, 2026
@version 1.0
"""

import boto3
from botocore.exceptions import ClientError
import os
import logging
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@athlynx.ai")

class EmailService:
    """AWS SES Email Service for ATHLYNX"""
    
    def __init__(self):
        self.client = boto3.client(
            'ses',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        self.sender = SENDER_EMAIL
    
    def send_verification_email(self, to_email: str, code: str, full_name: str) -> bool:
        """Send verification code email"""
        subject = "🦁 ATHLYNX - Verify Your Email"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; background-color: #0a1628; color: white; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 40px; }}
                .logo {{ text-align: center; margin-bottom: 30px; }}
                .code-box {{ 
                    background: linear-gradient(135deg, #00d4ff, #0066ff);
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    font-size: 32px;
                    letter-spacing: 8px;
                    font-weight: bold;
                    margin: 30px 0;
                }}
                .footer {{ text-align: center; margin-top: 40px; color: #888; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">
                    <h1>🦁 ATHLYNX AI</h1>
                    <p>The Athlete's Playbook</p>
                </div>
                
                <h2>Welcome, {full_name}!</h2>
                <p>Your verification code is:</p>
                
                <div class="code-box">{code}</div>
                
                <p>This code expires in 10 minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
                
                <div class="footer">
                    <p>Dreams Do Come True 2026! 🚀</p>
                    <p>© 2026 ATHLYNX AI Corporation</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        ATHLYNX AI - Email Verification
        
        Welcome, {full_name}!
        
        Your verification code is: {code}
        
        This code expires in 10 minutes.
        
        Dreams Do Come True 2026!
        © 2026 ATHLYNX AI Corporation
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    def send_welcome_email(self, to_email: str, full_name: str, waitlist_position: int) -> bool:
        """Send welcome email to new waitlist member"""
        subject = "🦁 Welcome to ATHLYNX VIP Waitlist!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; background-color: #0a1628; color: white; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 40px; }}
                .position-box {{ 
                    background: linear-gradient(135deg, #ffd700, #ff8c00);
                    padding: 30px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .position-number {{ font-size: 48px; font-weight: bold; }}
                .benefits {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; }}
                .benefit-item {{ padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🦁 Welcome to ATHLYNX AI!</h1>
                
                <p>Hey {full_name},</p>
                <p>You're officially on the VIP Waitlist!</p>
                
                <div class="position-box">
                    <p>Your Position</p>
                    <div class="position-number">#{waitlist_position}</div>
                    <p>of 10,000 Founding Members</p>
                </div>
                
                <div class="benefits">
                    <h3>🎁 Your VIP Benefits:</h3>
                    <div class="benefit-item">✅ 7 Days FREE VIP Access</div>
                    <div class="benefit-item">✅ Early Access to All 10 Apps</div>
                    <div class="benefit-item">✅ Exclusive NIL Opportunities</div>
                    <div class="benefit-item">✅ Founding Member Badge</div>
                    <div class="benefit-item">✅ Priority Support</div>
                </div>
                
                <p style="margin-top: 30px;">
                    <strong>Launch Date: February 1, 2026</strong>
                </p>
                
                <p>Dreams Do Come True 2026! 🚀</p>
                <p>- Chad Dozier & The ATHLYNX Team</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to ATHLYNX AI!
        
        Hey {full_name},
        
        You're officially on the VIP Waitlist!
        Your Position: #{waitlist_position} of 10,000 Founding Members
        
        Your VIP Benefits:
        - 7 Days FREE VIP Access
        - Early Access to All 10 Apps
        - Exclusive NIL Opportunities
        - Founding Member Badge
        - Priority Support
        
        Launch Date: February 1, 2026
        
        Dreams Do Come True 2026!
        - Chad Dozier & The ATHLYNX Team
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    def send_nil_deal_notification(self, to_email: str, full_name: str, brand_name: str, deal_value: float) -> bool:
        """Send NIL deal notification"""
        subject = f"🎉 New NIL Deal: {brand_name}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; background-color: #0a1628; color: white; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 40px; }}
                .deal-box {{ 
                    background: linear-gradient(135deg, #00ff88, #00d4ff);
                    padding: 30px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 30px 0;
                    color: #000;
                }}
                .deal-value {{ font-size: 48px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 Congratulations, {full_name}!</h1>
                
                <p>You have a new NIL deal opportunity!</p>
                
                <div class="deal-box">
                    <h2>{brand_name}</h2>
                    <div class="deal-value">${deal_value:,.2f}</div>
                </div>
                
                <p>Log in to your ATHLYNX dashboard to review and accept this deal.</p>
                
                <p>Dreams Do Come True 2026! 🚀</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Congratulations, {full_name}!
        
        You have a new NIL deal opportunity!
        
        Brand: {brand_name}
        Value: ${deal_value:,.2f}
        
        Log in to your ATHLYNX dashboard to review and accept this deal.
        
        Dreams Do Come True 2026!
        """
        
        return self._send_email(to_email, subject, html_body, text_body)
    
    def _send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        """Internal method to send email via AWS SES"""
        try:
            response = self.client.send_email(
                Source=self.sender,
                Destination={
                    'ToAddresses': [to_email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': text_body,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': html_body,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            
            logger.info(f"✅ Email sent to {to_email}: {response['MessageId']}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Email send error: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"❌ Email send error: {e}")
            return False

# Singleton instance
email_service = EmailService()
