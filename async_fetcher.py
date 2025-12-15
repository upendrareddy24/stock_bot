"""
Async API Fetcher for Stock Bot
Fetches multiple API endpoints in parallel for faster responses
"""
import asyncio
import aiohttp
from typing import List, Dict, Any
from cache_manager import cache

class AsyncFetcher:
    def __init__(self, timeout=10):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
    
    async def fetch_one(self, session: aiohttp.ClientSession, url: str, cache_key: str = None, cache_ttl: int = 300) -> Dict[str, Any]:
        """Fetch a single URL with caching"""
        # Check cache first
        if cache_key:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        
        try:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    # Cache the result
                    if cache_key:
                        cache.set(cache_key, data, cache_ttl)
                    return data
                else:
                    return {"error": f"HTTP {response.status}"}
        except asyncio.TimeoutError:
            return {"error": "Timeout"}
        except Exception as e:
            return {"error": str(e)}
    
    async def fetch_multiple(self, urls: List[tuple]) -> List[Dict[str, Any]]:
        """
        Fetch multiple URLs in parallel
        urls: List of (url, cache_key, cache_ttl) tuples
        """
        async with aiohttp.ClientSession() as session:
            tasks = []
            for item in urls:
                if len(item) == 3:
                    url, cache_key, cache_ttl = item
                elif len(item) == 2:
                    url, cache_key = item
                    cache_ttl = 300
                else:
                    url = item[0]
                    cache_key = None
                    cache_ttl = 300
                
                tasks.append(self.fetch_one(session, url, cache_key, cache_ttl))
            
            return await asyncio.gather(*tasks)
    
    def fetch_multiple_sync(self, urls: List[tuple]) -> List[Dict[str, Any]]:
        """Synchronous wrapper for async fetch_multiple"""
        return asyncio.run(self.fetch_multiple(urls))

# Global fetcher instance
fetcher = AsyncFetcher()
