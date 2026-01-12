"""
🦁 ATHLYNX AI - NIL Vault Router
Name, Image, Likeness Deal Management

@author ATHLYNX AI Corporation
@date January 12, 2026
@version 1.0
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, date
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/nil-vault", tags=["NIL Vault"])

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_8rFswVRXCg0c@ep-bold-bar-aegw1i6x-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@router.get("/")
async def get_nil_deals(
    athlete_id: int = None,
    status: str = None,
    deal_type: str = None,
    limit: int = 100,
    offset: int = 0
):
    """Get NIL deals with optional filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT nd.*, a.sport, u.full_name as athlete_name
            FROM nil_deals nd
            JOIN athletes a ON nd.athlete_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if athlete_id:
            query += " AND nd.athlete_id = %s"
            params.append(athlete_id)
        
        if status:
            query += " AND nd.status = %s"
            params.append(status)
        
        if deal_type:
            query += " AND nd.deal_type = %s"
            params.append(deal_type)
        
        query += " ORDER BY nd.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        deals = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "deals": [dict(d) for d in deals],
            "count": len(deals)
        }
        
    except Exception as e:
        logger.error(f"NIL deals list error: {e}")
        return {"success": False, "deals": [], "count": 0}

@router.post("/create")
async def create_nil_deal(request: Request):
    """Create a new NIL deal"""
    try:
        data = await request.json()
        
        athlete_id = data.get("athlete_id")
        brand_name = data.get("brand_name")
        deal_type = data.get("deal_type")
        value = data.get("value")
        description = data.get("description")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        if not all([athlete_id, brand_name, deal_type, value]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify athlete exists
        cursor.execute("SELECT id, nil_value FROM athletes WHERE id = %s", (athlete_id,))
        athlete = cursor.fetchone()
        
        if not athlete:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Athlete not found")
        
        # Create deal
        cursor.execute("""
            INSERT INTO nil_deals (athlete_id, brand_name, deal_type, value, description, 
                                   start_date, end_date, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', %s)
            RETURNING id
        """, (athlete_id, brand_name, deal_type, value, description, 
              start_date, end_date, datetime.now()))
        
        deal_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ NIL deal created: {brand_name} for athlete {athlete_id} - ${value}")
        
        return JSONResponse({
            "success": True,
            "message": "NIL deal created successfully",
            "deal_id": deal_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"NIL deal creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/accept/{deal_id}")
async def accept_nil_deal(deal_id: int):
    """Accept a NIL deal"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get deal info
        cursor.execute("""
            SELECT nd.*, a.nil_value as current_nil_value
            FROM nil_deals nd
            JOIN athletes a ON nd.athlete_id = a.id
            WHERE nd.id = %s AND nd.status = 'pending'
        """, (deal_id,))
        
        deal = cursor.fetchone()
        
        if not deal:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Deal not found or already processed")
        
        # Update deal status
        cursor.execute("""
            UPDATE nil_deals SET status = 'active' WHERE id = %s
        """, (deal_id,))
        
        # Update athlete's total NIL value
        new_nil_value = float(deal['current_nil_value'] or 0) + float(deal['value'])
        cursor.execute("""
            UPDATE athletes SET nil_value = %s WHERE id = %s
        """, (new_nil_value, deal['athlete_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ NIL deal {deal_id} accepted - ${deal['value']}")
        
        return JSONResponse({
            "success": True,
            "message": f"Deal accepted! Your total NIL value is now ${new_nil_value:,.2f}",
            "deal_value": float(deal['value']),
            "total_nil_value": new_nil_value
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"NIL deal accept error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reject/{deal_id}")
async def reject_nil_deal(deal_id: int, request: Request):
    """Reject a NIL deal"""
    try:
        data = await request.json()
        reason = data.get("reason", "No reason provided")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE nil_deals SET status = 'rejected' 
            WHERE id = %s AND status = 'pending'
            RETURNING id
        """, (deal_id,))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Deal not found or already processed")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ NIL deal {deal_id} rejected")
        
        return JSONResponse({
            "success": True,
            "message": "Deal rejected",
            "status": "rejected"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"NIL deal reject error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/athlete/{athlete_id}")
async def get_athlete_nil_summary(athlete_id: int):
    """Get NIL summary for an athlete"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get athlete info
        cursor.execute("""
            SELECT a.*, u.full_name
            FROM athletes a
            JOIN users u ON a.user_id = u.id
            WHERE a.id = %s
        """, (athlete_id,))
        
        athlete = cursor.fetchone()
        
        if not athlete:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Athlete not found")
        
        # Get deal stats
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE status = 'active') as active_deals,
                COUNT(*) FILTER (WHERE status = 'pending') as pending_deals,
                COUNT(*) FILTER (WHERE status = 'completed') as completed_deals,
                COALESCE(SUM(value) FILTER (WHERE status = 'active'), 0) as active_value,
                COALESCE(SUM(value) FILTER (WHERE status = 'completed'), 0) as completed_value
            FROM nil_deals
            WHERE athlete_id = %s
        """, (athlete_id,))
        
        stats = cursor.fetchone()
        
        # Get recent deals
        cursor.execute("""
            SELECT * FROM nil_deals
            WHERE athlete_id = %s
            ORDER BY created_at DESC
            LIMIT 10
        """, (athlete_id,))
        
        recent_deals = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "athlete": {
                "id": athlete['id'],
                "name": athlete['full_name'],
                "sport": athlete['sport'],
                "nil_value": float(athlete['nil_value'] or 0),
                "star_rating": athlete['star_rating']
            },
            "stats": {
                "active_deals": stats['active_deals'],
                "pending_deals": stats['pending_deals'],
                "completed_deals": stats['completed_deals'],
                "active_value": float(stats['active_value']),
                "completed_value": float(stats['completed_value']),
                "total_earnings": float(stats['active_value']) + float(stats['completed_value'])
            },
            "recent_deals": [dict(d) for d in recent_deals]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Athlete NIL summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marketplace")
async def get_nil_marketplace(
    sport: str = None,
    min_value: float = None,
    max_value: float = None
):
    """Get available NIL opportunities"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # This would typically show brand opportunities looking for athletes
        # For now, we'll show top athletes available for deals
        
        query = """
            SELECT a.*, u.full_name,
                   (SELECT COUNT(*) FROM nil_deals WHERE athlete_id = a.id AND status = 'active') as active_deals
            FROM athletes a
            JOIN users u ON a.user_id = u.id
            WHERE a.profile_complete = TRUE
        """
        params = []
        
        if sport:
            query += " AND a.sport = %s"
            params.append(sport)
        
        if min_value:
            query += " AND a.nil_value >= %s"
            params.append(min_value)
        
        if max_value:
            query += " AND a.nil_value <= %s"
            params.append(max_value)
        
        query += " ORDER BY a.star_rating DESC, a.nil_value DESC LIMIT 50"
        
        cursor.execute(query, params)
        athletes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "athletes": [dict(a) for a in athletes],
            "count": len(athletes)
        }
        
    except Exception as e:
        logger.error(f"NIL marketplace error: {e}")
        return {"success": False, "athletes": [], "count": 0}

@router.get("/stats")
async def get_nil_stats():
    """Get overall NIL statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total NIL value
        cursor.execute("""
            SELECT COALESCE(SUM(value), 0) as total
            FROM nil_deals
            WHERE status IN ('active', 'completed')
        """)
        total_value = cursor.fetchone()['total']
        
        # Average deal value
        cursor.execute("""
            SELECT COALESCE(AVG(value), 0) as avg
            FROM nil_deals
            WHERE status IN ('active', 'completed')
        """)
        avg_value = cursor.fetchone()['avg']
        
        # By sport
        cursor.execute("""
            SELECT a.sport, COALESCE(SUM(nd.value), 0) as total_value, COUNT(*) as deal_count
            FROM nil_deals nd
            JOIN athletes a ON nd.athlete_id = a.id
            WHERE nd.status IN ('active', 'completed')
            GROUP BY a.sport
            ORDER BY total_value DESC
        """)
        by_sport = cursor.fetchall()
        
        # Top earners
        cursor.execute("""
            SELECT u.full_name, a.sport, a.nil_value
            FROM athletes a
            JOIN users u ON a.user_id = u.id
            WHERE a.nil_value > 0
            ORDER BY a.nil_value DESC
            LIMIT 10
        """)
        top_earners = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "total_nil_value": float(total_value),
            "average_deal_value": float(avg_value),
            "by_sport": [dict(s) for s in by_sport],
            "top_earners": [dict(e) for e in top_earners]
        }
        
    except Exception as e:
        logger.error(f"NIL stats error: {e}")
        return {"total_nil_value": 0, "average_deal_value": 0, "by_sport": [], "top_earners": []}
