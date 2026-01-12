"""
🦁 ATHLYNX AI - API Routers Module
All FastAPI Route Handlers

@author ATHLYNX AI Corporation
@date January 12, 2026
"""

from .auth import router as auth_router
from .waitlist import router as waitlist_router
from .transfer_portal import router as transfer_portal_router
from .nil_vault import router as nil_vault_router
from .feed import router as feed_router
from .messages import router as messages_router

__all__ = [
    'auth_router',
    'waitlist_router',
    'transfer_portal_router',
    'nil_vault_router',
    'feed_router',
    'messages_router'
]
