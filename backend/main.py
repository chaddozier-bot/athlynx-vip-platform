"""
🦁 ATHLYNX AI - THE ATHLETE'S PLAYBOOK
100% Python + Julia Implementation
Built to make Chad Dozier the next billionaire!

Athlynx-AI-Start-Up-Launch-All-Phase-Beginning-Phase-1-2026-#14

@author ATHLYNX AI Corporation
@date January 12, 2026 - 4:00 PM CST
@version 2.0 - Pure Python/Julia Rebuild

Dreams Do Come True 2026! 🚀
"""

from fastapi import FastAPI, Request, HTTPException, Depends, Form, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime, timedelta
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import hashlib
import secrets
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APPLICATION INITIALIZATION
# ============================================================================

app = FastAPI(
    title="ATHLYNX AI - The Athlete's Playbook",
    description="The World's First Triple-Channel Verification Platform for Athletes",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates and static files configuration
templates = Jinja2Templates(directory="../frontend/templates")
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# ============================================================================
# DATABASE CONFIGURATION - NEON POSTGRESQL
# ============================================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_8rFswVRXCg0c@ep-bold-bar-aegw1i6x-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

def get_db_connection():
    """Get database connection to NEON PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def init_database():
    """Initialize database tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20),
                password_hash VARCHAR(255),
                full_name VARCHAR(255),
                role VARCHAR(50) DEFAULT 'user',
                sport VARCHAR(100),
                school VARCHAR(255),
                verified_email BOOLEAN DEFAULT FALSE,
                verified_phone BOOLEAN DEFAULT FALSE,
                verified_whatsapp BOOLEAN DEFAULT FALSE,
                vip_code VARCHAR(50),
                subscription_tier VARCHAR(50) DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Waitlist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS waitlist (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20),
                role VARCHAR(50),
                sport VARCHAR(100),
                referral_code VARCHAR(50),
                position INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Athletes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS athletes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                sport VARCHAR(100),
                position VARCHAR(100),
                school VARCHAR(255),
                graduation_year INTEGER,
                height VARCHAR(20),
                weight VARCHAR(20),
                gpa DECIMAL(3,2),
                nil_value DECIMAL(12,2) DEFAULT 0,
                star_rating INTEGER DEFAULT 0,
                profile_complete BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # NIL Deals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nil_deals (
                id SERIAL PRIMARY KEY,
                athlete_id INTEGER REFERENCES athletes(id),
                brand_name VARCHAR(255),
                deal_type VARCHAR(100),
                value DECIMAL(12,2),
                status VARCHAR(50) DEFAULT 'pending',
                start_date DATE,
                end_date DATE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Feed Posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feed_posts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                content TEXT,
                media_url VARCHAR(500),
                post_type VARCHAR(50) DEFAULT 'text',
                likes_count INTEGER DEFAULT 0,
                comments_count INTEGER DEFAULT 0,
                shares_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                sender_id INTEGER REFERENCES users(id),
                receiver_id INTEGER REFERENCES users(id),
                content TEXT,
                read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Verification codes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_codes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                email VARCHAR(255),
                phone VARCHAR(20),
                code VARCHAR(10),
                code_type VARCHAR(20),
                expires_at TIMESTAMP,
                used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                plan VARCHAR(50),
                status VARCHAR(50) DEFAULT 'active',
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                stripe_customer_id VARCHAR(255),
                stripe_subscription_id VARCHAR(255)
            )
        """)
        
        # Analytics events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_events (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                event_type VARCHAR(100),
                event_data JSONB,
                ip_address VARCHAR(50),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Transfer Portal table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transfer_portal (
                id SERIAL PRIMARY KEY,
                athlete_id INTEGER REFERENCES athletes(id),
                from_school VARCHAR(255),
                to_school VARCHAR(255),
                status VARCHAR(50) DEFAULT 'entered',
                entry_date DATE,
                commitment_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("✅ Database tables initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("🦁 ATHLYNX AI Starting Up...")
    init_database()
    logger.info("✅ ATHLYNX AI Ready - Dreams Do Come True 2026!")

# ============================================================================
# HOMEPAGE & MAIN ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """
    THE MASTERPIECE HOMEPAGE
    athlynxapp.vip design - The Canvas
    """
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "ATHLYNX - The Athlete's Playbook",
        "launch_date": "February 1, 2026",
        "founding_members": 10000,
        "apps_count": 10,
        "companies_count": 12
    })

@app.get("/chad-story", response_class=HTMLResponse)
@app.get("/the-story", response_class=HTMLResponse)
@app.get("/journey", response_class=HTMLResponse)
async def chad_story(request: Request):
    """
    THE BIG SCREEN STORY
    Chad Dozier's journey from Mississippi to Billionaire
    """
    return templates.TemplateResponse("chad_story.html", {
        "request": request,
        "title": "The Chad Dozier Story",
        "hero_image": "/static/images/CHAD_DOZIER_SIGNATURE_CARD.png"
    })

@app.get("/podcast", response_class=HTMLResponse)
@app.get("/podcast-hub", response_class=HTMLResponse)
@app.get("/show", response_class=HTMLResponse)
async def podcast_hub(request: Request):
    """
    TED TALK STYLE PODCAST HUB
    The Chad Dozier Show
    """
    episodes = [
        {
            "id": 1,
            "title": "The Perfect Storm: How It All Began",
            "description": "December 30, 2025, 11:54 PM. The night everything changed.",
            "duration": "42:18",
            "date": "January 1, 2026",
            "type": "video"
        },
        {
            "id": 2,
            "title": "The Cancer Crab Legacy",
            "description": "Family, faith, and fortune. The Dozier heritage.",
            "duration": "38:45",
            "date": "January 3, 2026",
            "type": "audio"
        },
        {
            "id": 3,
            "title": "12 Companies, One Vision",
            "description": "Building a $2 billion empire, one company at a time.",
            "duration": "51:22",
            "date": "January 5, 2026",
            "type": "video"
        }
    ]
    
    return templates.TemplateResponse("podcast_hub.html", {
        "request": request,
        "title": "The Chad Dozier Show",
        "episodes": episodes
    })

@app.get("/portal", response_class=HTMLResponse)
async def portal(request: Request):
    """ATHLYNX Portal - Main Dashboard"""
    return templates.TemplateResponse("portal.html", {
        "request": request,
        "title": "ATHLYNX Portal"
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login Page"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "title": "Login - ATHLYNX"
    })

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Signup Page"""
    return templates.TemplateResponse("signup.html", {
        "request": request,
        "title": "Sign Up - ATHLYNX"
    })

# ============================================================================
# VIP WAITLIST & EARLY ACCESS
# ============================================================================

@app.post("/api/waitlist")
async def join_waitlist(request: Request):
    """
    Join VIP Waitlist
    Triple-channel verification: Email + SMS + WhatsApp
    """
    try:
        data = await request.json()
        
        # Extract data
        full_name = data.get("full_name")
        email = data.get("email")
        phone = data.get("phone")
        role = data.get("role")
        sport = data.get("sport")
        
        # Validate
        if not all([full_name, email, phone]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get next position
        cursor.execute("SELECT COALESCE(MAX(position), 0) + 1 as next_pos FROM waitlist")
        next_position = cursor.fetchone()['next_pos']
        
        cursor.execute("""
            INSERT INTO waitlist (full_name, email, phone, role, sport, position, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (full_name, email, phone, role, sport, next_position, datetime.now()))
        
        waitlist_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ New waitlist signup: {email} (ID: {waitlist_id}, Position: {next_position})")
        
        # TODO: Send verification codes via AWS SES/SNS
        
        return JSONResponse({
            "success": True,
            "message": "Welcome to the VIP waitlist! Check your email and phone for verification codes.",
            "waitlist_id": waitlist_id,
            "position": next_position
        })
        
    except Exception as e:
        logger.error(f"Waitlist signup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/waitlist/count")
async def get_waitlist_count():
    """Get current waitlist count"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM waitlist")
        count = cursor.fetchone()['count']
        cursor.close()
        conn.close()
        return {"count": count}
    except Exception as e:
        logger.error(f"Error getting waitlist count: {e}")
        return {"count": 0}

# ============================================================================
# 10 ATHLYNX APPS
# ============================================================================

@app.get("/messenger", response_class=HTMLResponse)
async def messenger(request: Request):
    """App 1: ATHLYNX Messenger"""
    return templates.TemplateResponse("apps/messenger.html", {
        "request": request,
        "title": "ATHLYNX Messenger"
    })

@app.get("/diamond-grind", response_class=HTMLResponse)
async def diamond_grind(request: Request):
    """App 2: Diamond Grind"""
    return templates.TemplateResponse("apps/diamond_grind.html", {
        "request": request,
        "title": "Diamond Grind"
    })

@app.get("/warriors-playbook", response_class=HTMLResponse)
async def warriors_playbook(request: Request):
    """App 3: Warriors Playbook"""
    return templates.TemplateResponse("apps/warriors_playbook.html", {
        "request": request,
        "title": "Warriors Playbook"
    })

@app.get("/transfer-portal", response_class=HTMLResponse)
async def transfer_portal_page(request: Request):
    """App 4: Transfer Portal"""
    return templates.TemplateResponse("apps/transfer_portal.html", {
        "request": request,
        "title": "Transfer Portal"
    })

@app.get("/nil-vault", response_class=HTMLResponse)
async def nil_vault_page(request: Request):
    """App 5: NIL Vault"""
    return templates.TemplateResponse("apps/nil_vault.html", {
        "request": request,
        "title": "NIL Vault"
    })

@app.get("/ai-sales", response_class=HTMLResponse)
async def ai_sales(request: Request):
    """App 6: AI Sales"""
    return templates.TemplateResponse("apps/ai_sales.html", {
        "request": request,
        "title": "AI Sales"
    })

@app.get("/faith", response_class=HTMLResponse)
async def faith(request: Request):
    """App 7: Faith"""
    return templates.TemplateResponse("apps/faith.html", {
        "request": request,
        "title": "Faith"
    })

@app.get("/ai-recruiter", response_class=HTMLResponse)
async def ai_recruiter(request: Request):
    """App 8: AI Recruiter"""
    return templates.TemplateResponse("apps/ai_recruiter.html", {
        "request": request,
        "title": "AI Recruiter"
    })

@app.get("/ai-content", response_class=HTMLResponse)
async def ai_content(request: Request):
    """App 9: AI Content"""
    return templates.TemplateResponse("apps/ai_content.html", {
        "request": request,
        "title": "AI Content"
    })

@app.get("/infrastructure", response_class=HTMLResponse)
async def infrastructure(request: Request):
    """App 10: Infrastructure"""
    return templates.TemplateResponse("apps/infrastructure.html", {
        "request": request,
        "title": "Infrastructure"
    })

# ============================================================================
# AUTHENTICATION API
# ============================================================================

@app.post("/api/auth/register")
async def register(request: Request):
    """Register new user"""
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        full_name = data.get("full_name")
        phone = data.get("phone")
        
        if not all([email, password, full_name]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (email, password_hash, full_name, phone, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (email, password_hash, full_name, phone, datetime.now()))
        
        user_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ New user registered: {email} (ID: {user_id})")
        
        return JSONResponse({
            "success": True,
            "message": "Registration successful!",
            "user_id": user_id
        })
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
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
            SELECT id, email, full_name, role FROM users 
            WHERE email = %s AND password_hash = %s
        """, (email, password_hash))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate session token
        token = secrets.token_urlsafe(32)
        
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

# ============================================================================
# TRANSFER PORTAL API
# ============================================================================

@app.get("/api/transfer-portal")
async def get_transfer_portal_entries():
    """Get all transfer portal entries"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tp.*, a.sport, a.position, u.full_name
            FROM transfer_portal tp
            JOIN athletes a ON tp.athlete_id = a.id
            JOIN users u ON a.user_id = u.id
            ORDER BY tp.entry_date DESC
            LIMIT 100
        """)
        
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"entries": [dict(e) for e in entries]}
        
    except Exception as e:
        logger.error(f"Transfer portal error: {e}")
        return {"entries": []}

@app.post("/api/transfer-portal/enter")
async def enter_transfer_portal(request: Request):
    """Enter the transfer portal"""
    try:
        data = await request.json()
        athlete_id = data.get("athlete_id")
        from_school = data.get("from_school")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO transfer_portal (athlete_id, from_school, entry_date, status)
            VALUES (%s, %s, %s, 'entered')
            RETURNING id
        """, (athlete_id, from_school, datetime.now().date()))
        
        entry_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({
            "success": True,
            "message": "Successfully entered transfer portal",
            "entry_id": entry_id
        })
        
    except Exception as e:
        logger.error(f"Transfer portal entry error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# NIL VAULT API
# ============================================================================

@app.get("/api/nil-vault")
async def get_nil_deals():
    """Get NIL deals"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT nd.*, a.sport, u.full_name
            FROM nil_deals nd
            JOIN athletes a ON nd.athlete_id = a.id
            JOIN users u ON a.user_id = u.id
            ORDER BY nd.created_at DESC
            LIMIT 100
        """)
        
        deals = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"deals": [dict(d) for d in deals]}
        
    except Exception as e:
        logger.error(f"NIL vault error: {e}")
        return {"deals": []}

@app.post("/api/nil-vault/create")
async def create_nil_deal(request: Request):
    """Create new NIL deal"""
    try:
        data = await request.json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO nil_deals (athlete_id, brand_name, deal_type, value, description, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.get("athlete_id"),
            data.get("brand_name"),
            data.get("deal_type"),
            data.get("value"),
            data.get("description"),
            data.get("start_date"),
            data.get("end_date")
        ))
        
        deal_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({
            "success": True,
            "message": "NIL deal created successfully",
            "deal_id": deal_id
        })
        
    except Exception as e:
        logger.error(f"NIL deal creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FEED API
# ============================================================================

@app.get("/api/feed")
async def get_feed():
    """Get social feed posts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT fp.*, u.full_name, u.role
            FROM feed_posts fp
            JOIN users u ON fp.user_id = u.id
            ORDER BY fp.created_at DESC
            LIMIT 50
        """)
        
        posts = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"posts": [dict(p) for p in posts]}
        
    except Exception as e:
        logger.error(f"Feed error: {e}")
        return {"posts": []}

@app.post("/api/feed/post")
async def create_post(request: Request):
    """Create new feed post"""
    try:
        data = await request.json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO feed_posts (user_id, content, media_url, post_type)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            data.get("user_id"),
            data.get("content"),
            data.get("media_url"),
            data.get("post_type", "text")
        ))
        
        post_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({
            "success": True,
            "message": "Post created successfully",
            "post_id": post_id
        })
        
    except Exception as e:
        logger.error(f"Post creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MESSAGING API
# ============================================================================

@app.get("/api/messages/{user_id}")
async def get_messages(user_id: int):
    """Get messages for a user"""
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
            WHERE m.sender_id = %s OR m.receiver_id = %s
            ORDER BY m.created_at DESC
            LIMIT 100
        """, (user_id, user_id))
        
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {"messages": [dict(m) for m in messages]}
        
    except Exception as e:
        logger.error(f"Messages error: {e}")
        return {"messages": []}

@app.post("/api/messages/send")
async def send_message(request: Request):
    """Send a message"""
    try:
        data = await request.json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, content)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (
            data.get("sender_id"),
            data.get("receiver_id"),
            data.get("content")
        ))
        
        message_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({
            "success": True,
            "message": "Message sent successfully",
            "message_id": message_id
        })
        
    except Exception as e:
        logger.error(f"Message send error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HEALTH CHECK & STATS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "2.0.0",
        "project": "Athlynx-AI-Start-Up-Launch-All-Phase-Beginning-Phase-1-2026-#14"
    }

@app.get("/api/stats")
async def get_stats():
    """Get platform statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        stats["total_users"] = cursor.fetchone()['count']
        
        # Waitlist count
        cursor.execute("SELECT COUNT(*) as count FROM waitlist")
        stats["waitlist_count"] = cursor.fetchone()['count']
        
        # Athletes count
        cursor.execute("SELECT COUNT(*) as count FROM athletes")
        stats["athletes_count"] = cursor.fetchone()['count']
        
        # NIL deals count
        cursor.execute("SELECT COUNT(*) as count FROM nil_deals")
        stats["nil_deals_count"] = cursor.fetchone()['count']
        
        # Total NIL value
        cursor.execute("SELECT COALESCE(SUM(value), 0) as total FROM nil_deals WHERE status = 'active'")
        stats["total_nil_value"] = float(cursor.fetchone()['total'])
        
        # Posts count
        cursor.execute("SELECT COUNT(*) as count FROM feed_posts")
        stats["posts_count"] = cursor.fetchone()['count']
        
        # Messages count
        cursor.execute("SELECT COUNT(*) as count FROM messages")
        stats["messages_count"] = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        stats["timestamp"] = datetime.now().isoformat()
        
        return stats
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"error": str(e)}

# ============================================================================
# ANALYTICS TRACKING
# ============================================================================

@app.post("/api/analytics/track")
async def track_event(request: Request):
    """Track analytics event"""
    try:
        data = await request.json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO analytics_events (user_id, event_type, event_data, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data.get("user_id"),
            data.get("event_type"),
            json.dumps(data.get("event_data", {})),
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Analytics tracking error: {e}")
        return {"success": False}

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    print("""
    🦁 ═══════════════════════════════════════════════════════════════════════
    
       █████╗ ████████╗██╗  ██╗██╗  ██╗   ██╗███╗   ██╗██╗  ██╗
      ██╔══██╗╚══██╔══╝██║  ██║██║  ╚██╗ ██╔╝████╗  ██║╚██╗██╔╝
      ███████║   ██║   ███████║██║   ╚████╔╝ ██╔██╗ ██║ ╚███╔╝ 
      ██╔══██║   ██║   ██╔══██║██║    ╚██╔╝  ██║╚██╗██║ ██╔██╗ 
      ██║  ██║   ██║   ██║  ██║███████╗██║   ██║ ╚████║██╔╝ ██╗
      ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝
    
       THE ATHLETE'S PLAYBOOK - 100% Python + Julia
       Athlynx-AI-Start-Up-Launch-All-Phase-Beginning-Phase-1-2026-#14
       
       Dreams Do Come True 2026! 🚀
       
    ═══════════════════════════════════════════════════════════════════════ 🦁
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
