"""
🦁 ATHLYNX AI - Database Models & Schema
NEON PostgreSQL Database Configuration

@author ATHLYNX AI Corporation
@date January 12, 2026
@version 1.0
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_8rFswVRXCg0c@ep-bold-bar-aegw1i6x-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# Database Schema
SCHEMA = """
-- 🦁 ATHLYNX AI Database Schema
-- Athlynx-AI-Start-Up-Launch-All-Phase-Beginning-Phase-1-2026-#14

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    role VARCHAR(50) DEFAULT 'user',
    sport VARCHAR(100),
    profile_image_url TEXT,
    bio TEXT,
    verified_email BOOLEAN DEFAULT FALSE,
    verified_phone BOOLEAN DEFAULT FALSE,
    verified_whatsapp BOOLEAN DEFAULT FALSE,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Waitlist Table
CREATE TABLE IF NOT EXISTS waitlist (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    role VARCHAR(50),
    sport VARCHAR(100),
    position INTEGER NOT NULL,
    referral_code VARCHAR(50) UNIQUE,
    referred_by INTEGER REFERENCES waitlist(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Athletes Table
CREATE TABLE IF NOT EXISTS athletes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    sport VARCHAR(100) NOT NULL,
    position VARCHAR(100),
    school VARCHAR(255),
    graduation_year INTEGER,
    height VARCHAR(20),
    weight VARCHAR(20),
    gpa DECIMAL(3,2),
    star_rating INTEGER CHECK (star_rating >= 1 AND star_rating <= 5),
    nil_value DECIMAL(15,2) DEFAULT 0,
    profile_complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transfer Portal Table
CREATE TABLE IF NOT EXISTS transfer_portal (
    id SERIAL PRIMARY KEY,
    athlete_id INTEGER REFERENCES athletes(id) ON DELETE CASCADE,
    from_school VARCHAR(255) NOT NULL,
    to_school VARCHAR(255),
    status VARCHAR(50) DEFAULT 'entered',
    entry_date DATE NOT NULL,
    commitment_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NIL Deals Table
CREATE TABLE IF NOT EXISTS nil_deals (
    id SERIAL PRIMARY KEY,
    athlete_id INTEGER REFERENCES athletes(id) ON DELETE CASCADE,
    brand_name VARCHAR(255) NOT NULL,
    deal_type VARCHAR(100) NOT NULL,
    value DECIMAL(15,2) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feed Posts Table
CREATE TABLE IF NOT EXISTS feed_posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    media_url TEXT,
    post_type VARCHAR(50) DEFAULT 'text',
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages Table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    receiver_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verification Codes Table
CREATE TABLE IF NOT EXISTS verification_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    email VARCHAR(255),
    phone VARCHAR(50),
    code VARCHAR(20) NOT NULL,
    code_type VARCHAR(50) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subscriptions Table
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    plan VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    start_date DATE NOT NULL,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics Events Table
CREATE TABLE IF NOT EXISTS analytics_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_waitlist_email ON waitlist(email);
CREATE INDEX IF NOT EXISTS idx_waitlist_position ON waitlist(position);
CREATE INDEX IF NOT EXISTS idx_athletes_user_id ON athletes(user_id);
CREATE INDEX IF NOT EXISTS idx_athletes_sport ON athletes(sport);
CREATE INDEX IF NOT EXISTS idx_transfer_portal_athlete ON transfer_portal(athlete_id);
CREATE INDEX IF NOT EXISTS idx_transfer_portal_status ON transfer_portal(status);
CREATE INDEX IF NOT EXISTS idx_nil_deals_athlete ON nil_deals(athlete_id);
CREATE INDEX IF NOT EXISTS idx_nil_deals_status ON nil_deals(status);
CREATE INDEX IF NOT EXISTS idx_feed_posts_user ON feed_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_feed_posts_created ON feed_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_analytics_user ON analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_type ON analytics_events(event_type);
"""

def init_database():
    """Initialize database with schema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute schema
        cursor.execute(SCHEMA)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Database schema initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        return False

def check_database_connection():
    """Check if database is accessible"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result['test'] == 1
        
    except Exception as e:
        logger.error(f"❌ Database connection check failed: {e}")
        return False

if __name__ == "__main__":
    print("🦁 ATHLYNX AI - Database Initialization")
    print("Athlynx-AI-Start-Up-Launch-All-Phase-Beginning-Phase-1-2026-#14")
    print("-" * 50)
    
    if check_database_connection():
        print("✅ Database connection successful")
        
        if init_database():
            print("✅ Schema initialized")
        else:
            print("❌ Schema initialization failed")
    else:
        print("❌ Database connection failed")
