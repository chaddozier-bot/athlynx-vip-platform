"""
🦁 ATHLYNX AI - Messaging Router
Direct Messages and Conversations

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

router = APIRouter(prefix="/api/messages", tags=["Messaging"])

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_8rFswVRXCg0c@ep-bold-bar-aegw1i6x-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@router.get("/inbox/{user_id}")
async def get_inbox(user_id: int, limit: int = 50):
    """Get user's inbox messages"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.*, 
                   s.full_name as sender_name,
                   r.full_name as receiver_name
            FROM messages m
            JOIN users s ON m.sender_id = s.id
            JOIN users r ON m.receiver_id = r.id
            WHERE m.receiver_id = %s
            ORDER BY m.created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        messages = cursor.fetchall()
        
        # Count unread
        cursor.execute("""
            SELECT COUNT(*) as unread FROM messages
            WHERE receiver_id = %s AND read = FALSE
        """, (user_id,))
        unread_count = cursor.fetchone()['unread']
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "messages": [dict(m) for m in messages],
            "unread_count": unread_count
        }
        
    except Exception as e:
        logger.error(f"Inbox error: {e}")
        return {"success": False, "messages": [], "unread_count": 0}

@router.get("/sent/{user_id}")
async def get_sent_messages(user_id: int, limit: int = 50):
    """Get user's sent messages"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.*, 
                   s.full_name as sender_name,
                   r.full_name as receiver_name
            FROM messages m
            JOIN users s ON m.sender_id = s.id
            JOIN users r ON m.receiver_id = r.id
            WHERE m.sender_id = %s
            ORDER BY m.created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        messages = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "messages": [dict(m) for m in messages]
        }
        
    except Exception as e:
        logger.error(f"Sent messages error: {e}")
        return {"success": False, "messages": []}

@router.get("/conversation/{user_id}/{other_user_id}")
async def get_conversation(user_id: int, other_user_id: int, limit: int = 100):
    """Get conversation between two users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.*, 
                   s.full_name as sender_name,
                   r.full_name as receiver_name
            FROM messages m
            JOIN users s ON m.sender_id = s.id
            JOIN users r ON m.receiver_id = r.id
            WHERE (m.sender_id = %s AND m.receiver_id = %s)
               OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.created_at ASC
            LIMIT %s
        """, (user_id, other_user_id, other_user_id, user_id, limit))
        
        messages = cursor.fetchall()
        
        # Mark messages as read
        cursor.execute("""
            UPDATE messages SET read = TRUE
            WHERE receiver_id = %s AND sender_id = %s AND read = FALSE
        """, (user_id, other_user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "messages": [dict(m) for m in messages]
        }
        
    except Exception as e:
        logger.error(f"Conversation error: {e}")
        return {"success": False, "messages": []}

@router.post("/send")
async def send_message(request: Request):
    """Send a message"""
    try:
        data = await request.json()
        
        sender_id = data.get("sender_id")
        receiver_id = data.get("receiver_id")
        content = data.get("content")
        
        if not all([sender_id, receiver_id, content]):
            raise HTTPException(status_code=400, detail="Sender, receiver, and content required")
        
        if sender_id == receiver_id:
            raise HTTPException(status_code=400, detail="Cannot send message to yourself")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify both users exist
        cursor.execute("SELECT id FROM users WHERE id IN (%s, %s)", (sender_id, receiver_id))
        users = cursor.fetchall()
        
        if len(users) != 2:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="One or both users not found")
        
        # Send message
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, content, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (sender_id, receiver_id, content, datetime.now()))
        
        message_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Message sent from {sender_id} to {receiver_id}")
        
        return JSONResponse({
            "success": True,
            "message": "Message sent successfully",
            "message_id": message_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/read/{message_id}")
async def mark_as_read(message_id: int, request: Request):
    """Mark a message as read"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE messages SET read = TRUE
            WHERE id = %s AND receiver_id = %s
            RETURNING id
        """, (message_id, user_id))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Message not found or unauthorized")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({
            "success": True,
            "message": "Message marked as read"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mark read error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{message_id}")
async def delete_message(message_id: int, request: Request):
    """Delete a message"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Only allow deletion by sender or receiver
        cursor.execute("""
            DELETE FROM messages 
            WHERE id = %s AND (sender_id = %s OR receiver_id = %s)
            RETURNING id
        """, (message_id, user_id, user_id))
        
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Message not found or unauthorized")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Message {message_id} deleted")
        
        return JSONResponse({
            "success": True,
            "message": "Message deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{user_id}")
async def get_conversations_list(user_id: int):
    """Get list of all conversations for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get unique conversation partners with last message
        cursor.execute("""
            WITH conversation_partners AS (
                SELECT DISTINCT
                    CASE 
                        WHEN sender_id = %s THEN receiver_id 
                        ELSE sender_id 
                    END as partner_id
                FROM messages
                WHERE sender_id = %s OR receiver_id = %s
            )
            SELECT 
                cp.partner_id,
                u.full_name as partner_name,
                (
                    SELECT content FROM messages 
                    WHERE (sender_id = %s AND receiver_id = cp.partner_id)
                       OR (sender_id = cp.partner_id AND receiver_id = %s)
                    ORDER BY created_at DESC LIMIT 1
                ) as last_message,
                (
                    SELECT created_at FROM messages 
                    WHERE (sender_id = %s AND receiver_id = cp.partner_id)
                       OR (sender_id = cp.partner_id AND receiver_id = %s)
                    ORDER BY created_at DESC LIMIT 1
                ) as last_message_time,
                (
                    SELECT COUNT(*) FROM messages 
                    WHERE sender_id = cp.partner_id AND receiver_id = %s AND read = FALSE
                ) as unread_count
            FROM conversation_partners cp
            JOIN users u ON cp.partner_id = u.id
            ORDER BY last_message_time DESC
        """, (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id))
        
        conversations = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "conversations": [dict(c) for c in conversations]
        }
        
    except Exception as e:
        logger.error(f"Conversations list error: {e}")
        return {"success": False, "conversations": []}

@router.get("/unread-count/{user_id}")
async def get_unread_count(user_id: int):
    """Get total unread message count"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM messages
            WHERE receiver_id = %s AND read = FALSE
        """, (user_id,))
        
        count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return {"unread_count": count}
        
    except Exception as e:
        logger.error(f"Unread count error: {e}")
        return {"unread_count": 0}
