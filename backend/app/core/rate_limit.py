"""
Simple Rate Limiting Implementation
For production, consider using slowapi or redis-based rate limiting
"""
from fastapi import HTTPException, Request
from collections import defaultdict
import time
from typing import Dict

# In-memory store (use Redis in production)
request_counts: Dict[str, list] = defaultdict(list)

def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """
    Simple rate limiting decorator
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            current_time = time.time()
            
            # Clean old requests
            request_counts[client_ip] = [
                t for t in request_counts[client_ip] 
                if current_time - t < window_seconds
            ]
            
            if len(request_counts[client_ip]) >= max_requests:
                raise HTTPException(
                    status_code=429, 
                    detail="Too many requests. Please try again later."
                )
            
            request_counts[client_ip].append(current_time)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator