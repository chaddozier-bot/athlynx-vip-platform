"""
🦁 ATHLYNX AI - Database Models & Schema
PlanetScale PostgreSQL → NEON PostgreSQL (Final Destination)

Deployment Chain: GitHub → Manus → PlanetScale → Netlify → NEON

@author ATHLYNX AI Corporation
@date January 15, 2026
@version 2.0
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging

logger = logging.getLogger(__name__)

# All credentials from environment variables only
PLANETSCALE_HOST = os.getenv("DATABASE_HOST")
PLANETSCALE_PORT = os.getenv("DATABASE_PORT", "6432")
PLANETSCALE_USER = os.getenv("DATABASE_USERNAME")
PLANETSCALE_PASSWORD = os.getenv("DATABASE_PASSWORD")
PLANETSCALE_DB = os.getenv("DATABASE", "postgres")

# NEON Configuration (Final Production Destination)
NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL")
DATABASE_URL = os.getenv("DATABASE_URL")

# Check which database to use
USE_NEON = os.getenv("USE_NEON", "false").lower() == "true"

def get_db_connection():
    """Get database connection - Priority: NEON → DATABASE_URL → PlanetScale"""
    try:
        if USE_NEON and NEON_DATABASE_URL:
            logger.info("🔗 Connecting to NEON (Final Destination)")
            return psycopg2.connect(NEON_DATABASE_URL, cursor_factory=RealDictCursor)
        
        if DATABASE_URL:
            logger.info("🔗 Connecting via DATABASE_URL")
            return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        
        if PLANETSCALE_HOST and PLANETSCALE_USER and PLANETSCALE_PASSWORD:
            logger.info("🔗 Connecting to PlanetScale")
            return psycopg2.connect(
                host=PLANETSCALE_HOST,
                port=PLANETSCALE_PORT,
                user=PLANETSCALE_USER,
                password=PLANETSCALE_PASSWORD,
                dbname=PLANETSCALE_DB,
                sslmode='require',
                cursor_factory=RealDictCursor
            )
        
        raise ValueError("No database credentials configured")
        
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        raise

SCHEMA = """
-- 🦁 ATHLYNX AI Database Schema
CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, email VARCHAR(255) UNIQUE NOT NULL, password_hash VARCHAR(255), full_name VARCHAR(255), phone VARCHAR(50), role VARCHAR(50) DEFAULT 'user', sport VARCHAR(100), verified_email BOOLEAN DEFAULT FALSE, verified_phone BOOLEAN DEFAULT FALSE, subscription_tier VARCHAR(50) DEFAULT 'free', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS waitlist (id SERIAL PRIMARY KEY, full_name VARCHAR(255) NOT NULL, email VARCHAR(255) UNIQUE NOT NULL, phone VARCHAR(50), role VARCHAR(50), sport VARCHAR(100), position INTEGER NOT NULL, referral_code VARCHAR(50) UNIQUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS athletes (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id), sport VARCHAR(100), school VARCHAR(255), star_rating INTEGER, nil_value DECIMAL(15,2) DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS transfer_portal (id SERIAL PRIMARY KEY, athlete_id INTEGER REFERENCES athletes(id), from_school VARCHAR(255), to_school VARCHAR(255), status VARCHAR(50) DEFAULT 'entered', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS nil_deals (id SERIAL PRIMARY KEY, athlete_id INTEGER REFERENCES athletes(id), brand_name VARCHAR(255), value DECIMAL(15,2), status VARCHAR(50) DEFAULT 'pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS verification_codes (id SERIAL PRIMARY KEY, email VARCHAR(255), phone VARCHAR(50), code VARCHAR(20) NOT NULL, expires_at TIMESTAMP NOT NULL, used BOOLEAN DEFAULT FALSE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS vip_codes (id SERIAL PRIMARY KEY, code VARCHAR(50) UNIQUE NOT NULL, max_uses INTEGER DEFAULT 100, current_uses INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
"""

def init_database():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(SCHEMA)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("✅ Database initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Init error: {e}")
        return False

def check_database_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result['test'] == 1
    except Exception as e:
        logger.error(f"❌ Connection check failed: {e}")
        return False

if __name__ == "__main__":
    print("🦁 ATHLYNX AI - Database Check")
    if check_database_connection():
        print("✅ Connected!")
        init_database()
    else:
        print("❌ Connection failed")
