"""
🦁 ATHLYNX AI - Transfer Portal Router
College Athlete Transfer Management

@author ATHLYNX AI Corporation
@date January 12, 2026
@version 1.0
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/transfer-portal", tags=["Transfer Portal"])

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_8rFswVRXCg0c@ep-bold-bar-aegw1i6x-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@router.get("/")
async def get_transfer_portal_entries(
    sport: str = None,
    status: str = None,
    limit: int = 100,
    offset: int = 0
):
    """Get transfer portal entries with optional filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT tp.*, a.sport, a.position as player_position, a.star_rating,
                   u.full_name, a.graduation_year
            FROM transfer_portal tp
            JOIN athletes a ON tp.athlete_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if sport:
            query += " AND a.sport = %s"
            params.append(sport)
        
        if status:
            query += " AND tp.status = %s"
            params.append(status)
        
        query += " ORDER BY tp.entry_date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        entries = cursor.fetchall()
        
        # Get total count
        count_query = """
            SELECT COUNT(*) as total
            FROM transfer_portal tp
            JOIN athletes a ON tp.athlete_id = a.id
            WHERE 1=1
        """
        count_params = []
        
        if sport:
            count_query += " AND a.sport = %s"
            count_params.append(sport)
        
        if status:
            count_query += " AND tp.status = %s"
            count_params.append(status)
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "entries": [dict(e) for e in entries],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Transfer portal list error: {e}")
        return {"success": False, "entries": [], "total": 0}

@router.post("/enter")
async def enter_transfer_portal(request: Request):
    """Enter the transfer portal"""
    try:
        data = await request.json()
        
        athlete_id = data.get("athlete_id")
        from_school = data.get("from_school")
        reason = data.get("reason")
        
        if not all([athlete_id, from_school]):
            raise HTTPException(status_code=400, detail="Athlete ID and current school required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if athlete exists
        cursor.execute("SELECT id FROM athletes WHERE id = %s", (athlete_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Athlete not found")
        
        # Check if already in portal
        cursor.execute("""
            SELECT id FROM transfer_portal 
            WHERE athlete_id = %s AND status IN ('entered', 'exploring')
        """, (athlete_id,))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Athlete already in transfer portal")
        
        # Enter portal
        cursor.execute("""
            INSERT INTO transfer_portal (athlete_id, from_school, status, entry_date, created_at)
            VALUES (%s, %s, 'entered', %s, %s)
            RETURNING id
        """, (athlete_id, from_school, date.today(), datetime.now()))
        
        entry_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Athlete {athlete_id} entered transfer portal from {from_school}")
        
        return JSONResponse({
            "success": True,
            "message": "Successfully entered the transfer portal",
            "entry_id": entry_id,
            "status": "entered"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transfer portal entry error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/commit")
async def commit_to_school(request: Request):
    """Commit to a new school"""
    try:
        data = await request.json()
        
        entry_id = data.get("entry_id")
        to_school = data.get("to_school")
        
        if not all([entry_id, to_school]):
            raise HTTPException(status_code=400, detail="Entry ID and destination school required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update portal entry
        cursor.execute("""
            UPDATE transfer_portal 
            SET to_school = %s, status = 'committed', commitment_date = %s
            WHERE id = %s AND status IN ('entered', 'exploring')
            RETURNING id, athlete_id
        """, (to_school, date.today(), entry_id))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Portal entry not found or already committed")
        
        # Update athlete's school
        cursor.execute("""
            UPDATE athletes SET school = %s WHERE id = %s
        """, (to_school, result['athlete_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Athlete committed to {to_school}")
        
        return JSONResponse({
            "success": True,
            "message": f"Congratulations! Committed to {to_school}!",
            "status": "committed",
            "school": to_school
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Commitment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/withdraw")
async def withdraw_from_portal(request: Request):
    """Withdraw from transfer portal"""
    try:
        data = await request.json()
        entry_id = data.get("entry_id")
        
        if not entry_id:
            raise HTTPException(status_code=400, detail="Entry ID required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE transfer_portal 
            SET status = 'withdrawn'
            WHERE id = %s AND status IN ('entered', 'exploring')
            RETURNING id
        """, (entry_id,))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Portal entry not found or cannot be withdrawn")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Portal entry {entry_id} withdrawn")
        
        return JSONResponse({
            "success": True,
            "message": "Successfully withdrawn from transfer portal",
            "status": "withdrawn"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Withdrawal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_transfer_portal_stats():
    """Get transfer portal statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total in portal
        cursor.execute("SELECT COUNT(*) as total FROM transfer_portal WHERE status = 'entered'")
        in_portal = cursor.fetchone()['total']
        
        # Committed this year
        cursor.execute("""
            SELECT COUNT(*) as total FROM transfer_portal 
            WHERE status = 'committed' AND EXTRACT(YEAR FROM commitment_date) = EXTRACT(YEAR FROM CURRENT_DATE)
        """)
        committed = cursor.fetchone()['total']
        
        # By sport
        cursor.execute("""
            SELECT a.sport, COUNT(*) as count
            FROM transfer_portal tp
            JOIN athletes a ON tp.athlete_id = a.id
            WHERE tp.status = 'entered'
            GROUP BY a.sport
            ORDER BY count DESC
        """)
        by_sport = cursor.fetchall()
        
        # Top destination schools
        cursor.execute("""
            SELECT to_school, COUNT(*) as count
            FROM transfer_portal
            WHERE status = 'committed' AND to_school IS NOT NULL
            GROUP BY to_school
            ORDER BY count DESC
            LIMIT 10
        """)
        top_destinations = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "in_portal": in_portal,
            "committed_this_year": committed,
            "by_sport": [dict(s) for s in by_sport],
            "top_destinations": [dict(d) for d in top_destinations]
        }
        
    except Exception as e:
        logger.error(f"Transfer portal stats error: {e}")
        return {"in_portal": 0, "committed_this_year": 0, "by_sport": [], "top_destinations": []}

@router.get("/search")
async def search_transfer_portal(
    query: str = None,
    sport: str = None,
    position: str = None,
    min_stars: int = None
):
    """Search transfer portal athletes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """
            SELECT tp.*, a.sport, a.position as player_position, a.star_rating,
                   u.full_name, a.graduation_year, a.height, a.weight, a.gpa
            FROM transfer_portal tp
            JOIN athletes a ON tp.athlete_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE tp.status = 'entered'
        """
        params = []
        
        if query:
            sql += " AND (u.full_name ILIKE %s OR tp.from_school ILIKE %s)"
            params.extend([f"%{query}%", f"%{query}%"])
        
        if sport:
            sql += " AND a.sport = %s"
            params.append(sport)
        
        if position:
            sql += " AND a.position = %s"
            params.append(position)
        
        if min_stars:
            sql += " AND a.star_rating >= %s"
            params.append(min_stars)
        
        sql += " ORDER BY a.star_rating DESC, tp.entry_date DESC LIMIT 50"
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "results": [dict(r) for r in results],
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Transfer portal search error: {e}")
        return {"success": False, "results": [], "count": 0}
