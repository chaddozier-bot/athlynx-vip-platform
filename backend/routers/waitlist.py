"""
🦁 ATHLYNX AI - VIP Waitlist Router
Early Access & Founding Members

@author ATHLYNX AI Corporation
@date January 12, 2026
@version 1.0
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
import secrets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/waitlist", tags=["Waitlist"])

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_8rFswVRXCg0c@ep-bold-bar-aegw1i6x-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@router.post("/join")
async def join_waitlist(request: Request):
    """Join the VIP waitlist"""
    try:
        data = await request.json()
        
        full_name = data.get("full_name")
        email = data.get("email")
        phone = data.get("phone")
        role = data.get("role")
        sport = data.get("sport")
        
        if not all([full_name, email]):
            raise HTTPException(status_code=400, detail="Name and email are required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if already on waitlist
        cursor.execute("SELECT id, position FROM waitlist WHERE email = %s", (email,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.close()
            conn.close()
            return JSONResponse({
                "success": True,
                "message": f"You're already on the waitlist at position #{existing['position']}!",
                "position": existing['position'],
                "already_registered": True
            })
        
        # Get next position
        cursor.execute("SELECT COALESCE(MAX(position), 0) + 1 as next_pos FROM waitlist")
        next_position = cursor.fetchone()['next_pos']
        
        # Generate referral code
        referral_code = f"ATHLYNX-{secrets.token_hex(4).upper()}"
        
        # Insert into waitlist
        cursor.execute("""
            INSERT INTO waitlist (full_name, email, phone, role, sport, position, referral_code, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (full_name, email, phone, role, sport, next_position, referral_code, datetime.now()))
        
        waitlist_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ New waitlist signup: {email} (Position: {next_position})")
        
        # TODO: Send welcome email and SMS via AWS SES/SNS
        
        return JSONResponse({
            "success": True,
            "message": f"Welcome to the VIP waitlist! You're #{next_position} of 10,000 founding members!",
            "waitlist_id": waitlist_id,
            "position": next_position,
            "referral_code": referral_code
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Waitlist join error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/count")
async def get_waitlist_count():
    """Get current waitlist count"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM waitlist")
        count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return {
            "count": count,
            "remaining": max(0, 10000 - count),
            "percent_full": min(100, (count / 10000) * 100)
        }
        
    except Exception as e:
        logger.error(f"Waitlist count error: {e}")
        return {"count": 0, "remaining": 10000, "percent_full": 0}

@router.get("/position/{email}")
async def get_waitlist_position(email: str):
    """Get waitlist position by email"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, full_name, position, referral_code, created_at
            FROM waitlist WHERE email = %s
        """, (email,))
        
        entry = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Email not found on waitlist")
        
        return {
            "success": True,
            "position": entry['position'],
            "full_name": entry['full_name'],
            "referral_code": entry['referral_code'],
            "joined_at": entry['created_at'].isoformat() if entry['created_at'] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get position error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/referral")
async def apply_referral(request: Request):
    """Apply a referral code to move up in the waitlist"""
    try:
        data = await request.json()
        
        email = data.get("email")
        referral_code = data.get("referral_code")
        
        if not all([email, referral_code]):
            raise HTTPException(status_code=400, detail="Email and referral code required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find referrer
        cursor.execute("SELECT id, email FROM waitlist WHERE referral_code = %s", (referral_code,))
        referrer = cursor.fetchone()
        
        if not referrer:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid referral code")
        
        if referrer['email'] == email:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Cannot use your own referral code")
        
        # Find the person applying the code
        cursor.execute("SELECT id, position FROM waitlist WHERE email = %s", (email,))
        applicant = cursor.fetchone()
        
        if not applicant:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Email not found on waitlist")
        
        # Move applicant up 10 positions (minimum position is 1)
        new_position = max(1, applicant['position'] - 10)
        
        cursor.execute("""
            UPDATE waitlist SET position = %s WHERE id = %s
        """, (new_position, applicant['id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Referral applied: {email} moved from #{applicant['position']} to #{new_position}")
        
        return JSONResponse({
            "success": True,
            "message": f"Referral applied! You moved from #{applicant['position']} to #{new_position}!",
            "old_position": applicant['position'],
            "new_position": new_position,
            "positions_gained": applicant['position'] - new_position
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Referral error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaderboard")
async def get_waitlist_leaderboard():
    """Get top 100 waitlist members"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT full_name, position, role, sport, created_at
            FROM waitlist
            ORDER BY position ASC
            LIMIT 100
        """)
        
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "leaderboard": [
                {
                    "position": e['position'],
                    "name": e['full_name'],
                    "role": e['role'],
                    "sport": e['sport'],
                    "joined": e['created_at'].isoformat() if e['created_at'] else None
                }
                for e in entries
            ]
        }
        
    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        return {"success": False, "leaderboard": []}

@router.get("/stats")
async def get_waitlist_stats():
    """Get waitlist statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total count
        cursor.execute("SELECT COUNT(*) as total FROM waitlist")
        total = cursor.fetchone()['total']
        
        # By role
        cursor.execute("""
            SELECT role, COUNT(*) as count
            FROM waitlist
            WHERE role IS NOT NULL
            GROUP BY role
            ORDER BY count DESC
        """)
        by_role = cursor.fetchall()
        
        # By sport
        cursor.execute("""
            SELECT sport, COUNT(*) as count
            FROM waitlist
            WHERE sport IS NOT NULL
            GROUP BY sport
            ORDER BY count DESC
            LIMIT 10
        """)
        by_sport = cursor.fetchall()
        
        # Today's signups
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM waitlist
            WHERE DATE(created_at) = CURRENT_DATE
        """)
        today = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return {
            "total": total,
            "remaining_spots": max(0, 10000 - total),
            "today_signups": today,
            "by_role": [dict(r) for r in by_role],
            "by_sport": [dict(s) for s in by_sport]
        }
        
    except Exception as e:
        logger.error(f"Waitlist stats error: {e}")
        return {"total": 0, "remaining_spots": 10000, "today_signups": 0, "by_role": [], "by_sport": []}
