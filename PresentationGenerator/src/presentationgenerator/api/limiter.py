"""
Shared Rate Limiter instance for SlowAPI across all routers and the main application.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Global limiter instance identifying clients by their remote IP address
limiter = Limiter(key_func=get_remote_address)
