import time
from typing import Any, Optional

class TTLCache:
    
    def __init__(self, default_ttl: int = 60):

        self.default_ttl = default_ttl
        self._store = {}  

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        expires_at, value = self._store[key]
        if expires_at < time.time():
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if ttl is None:
            ttl = self.default_ttl
        expires_at = time.time() + ttl
        self._store[key] = (expires_at, value)

    def clear(self) -> None:
        self._store.clear()

    def clean_expired(self) -> int:
        now = time.time()
        expired_keys = [k for k, (exp, _) in self._store.items() if exp < now]
        for k in expired_keys:
            del self._store[k]
        return len(expired_keys)

search_cache = TTLCache(default_ttl=60)  