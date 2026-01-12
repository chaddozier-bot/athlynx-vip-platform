"""
🦁 ATHLYNX AI - Social Feed Router
Posts, Likes, Comments, and Shares

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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feed", tags=["Social Feed"])

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_8rFswVRXCg0c@ep-bold-bar-aegw1i6x-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@router.get("/")
async def get_feed(limit: int = 50, offset: int = 0, user_id: int = None):
    """Get social feed posts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT fp.*, u.full_name, u.role
            FROM feed_posts fp
            JOIN users u ON fp.user_id = u.id
        """
        params = []
        
        if user_id:
            query += " WHERE fp.user_id = %s"
            params.append(user_id)
        
        query += " ORDER BY fp.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        posts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "posts": [dict(p) for p in posts],
            "count": len(posts)
        }
        
    except Exception as e:
        logger.error(f"Feed error: {e}")
        return {"success": False, "posts": [], "count": 0}

@router.post("/post")
async def create_post(request: Request):
    """Create a new post"""
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        content = data.get("content")
        media_url = data.get("media_url")
        post_type = data.get("post_type", "text")
        
        if not user_id or not content:
            raise HTTPException(status_code=400, detail="User ID and content required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO feed_posts (user_id, content, media_url, post_type, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, content, media_url, post_type, datetime.now()))
        
        post_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ New post created by user {user_id}")
        
        return JSONResponse({
            "success": True,
            "message": "Post created successfully",
            "post_id": post_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Post creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/like/{post_id}")
async def like_post(post_id: int, request: Request):
    """Like a post"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Increment likes count
        cursor.execute("""
            UPDATE feed_posts 
            SET likes_count = likes_count + 1
            WHERE id = %s
            RETURNING likes_count
        """, (post_id,))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Post not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({
            "success": True,
            "likes_count": result['likes_count']
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Like error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/unlike/{post_id}")
async def unlike_post(post_id: int, request: Request):
    """Unlike a post"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Decrement likes count (minimum 0)
        cursor.execute("""
            UPDATE feed_posts 
            SET likes_count = GREATEST(0, likes_count - 1)
            WHERE id = %s
            RETURNING likes_count
        """, (post_id,))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Post not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({
            "success": True,
            "likes_count": result['likes_count']
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unlike error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/share/{post_id}")
async def share_post(post_id: int, request: Request):
    """Share a post"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Increment shares count
        cursor.execute("""
            UPDATE feed_posts 
            SET shares_count = shares_count + 1
            WHERE id = %s
            RETURNING shares_count
        """, (post_id,))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Post not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({
            "success": True,
            "shares_count": result['shares_count']
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Share error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{post_id}")
async def delete_post(post_id: int, request: Request):
    """Delete a post"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Only allow deletion by post owner
        cursor.execute("""
            DELETE FROM feed_posts 
            WHERE id = %s AND user_id = %s
            RETURNING id
        """, (post_id, user_id))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Post not found or unauthorized")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Post {post_id} deleted by user {user_id}")
        
        return JSONResponse({
            "success": True,
            "message": "Post deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete post error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending")
async def get_trending_posts(limit: int = 20):
    """Get trending posts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get posts with most engagement in last 24 hours
        cursor.execute("""
            SELECT fp.*, u.full_name, u.role,
                   (fp.likes_count + fp.comments_count * 2 + fp.shares_count * 3) as engagement_score
            FROM feed_posts fp
            JOIN users u ON fp.user_id = u.id
            WHERE fp.created_at > NOW() - INTERVAL '24 hours'
            ORDER BY engagement_score DESC
            LIMIT %s
        """, (limit,))
        
        posts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "trending": [dict(p) for p in posts]
        }
        
    except Exception as e:
        logger.error(f"Trending error: {e}")
        return {"success": False, "trending": []}

@router.get("/user/{user_id}")
async def get_user_posts(user_id: int, limit: int = 50):
    """Get posts by a specific user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT fp.*, u.full_name, u.role
            FROM feed_posts fp
            JOIN users u ON fp.user_id = u.id
            WHERE fp.user_id = %s
            ORDER BY fp.created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        posts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "posts": [dict(p) for p in posts],
            "count": len(posts)
        }
        
    except Exception as e:
        logger.error(f"User posts error: {e}")
        return {"success": False, "posts": [], "count": 0}
