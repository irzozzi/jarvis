import json
import redis
from functools import wraps
from typing import Any, Callable, Awaitable
from fastapi import Request
import asyncio

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_key_builder(request: Request) -> str:
    path = request.url.path
    query = request.url.query
    return f"{path}:{query}" if query else path

def cache(ttl: int = 300):
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get('request')
            if not request:
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

            try:
                key = cache_key_builder(request)
                cached = redis_client.get(key)
                if cached:
                    return json.loads(cached)
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                redis_client.setex(key, ttl, json.dumps(result, default=str))
                return result
            except redis.ConnectionError:
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get('request')
            if not request:
                return func(*args, **kwargs)

            try:
                key = cache_key_builder(request)
                cached = redis_client.get(key)
                if cached:
                    return json.loads(cached)
                result = func(*args, **kwargs)
                redis_client.setex(key, ttl, json.dumps(result, default=str))
                return result
            except redis.ConnectionError:
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def invalidate_pattern(pattern: str = "/*"):
    try:
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
    except redis.ConnectionError:
        pass