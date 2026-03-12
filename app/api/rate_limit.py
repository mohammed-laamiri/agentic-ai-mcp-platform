"""
Rate limiting configuration for Phase 4.3.

- Uses SlowAPI Limiter
- Can be applied globally (middleware) or per-route
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Limiter instance using remote IP as key
limiter = Limiter(key_func=get_remote_address)