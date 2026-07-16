import time
import hashlib
from typing import Optional, Dict, Any
from threading import Lock
from config.settings import settings


class CacheEntry:
    """Запись в кеше с TTL"""
    
    def __init__(self, value: str, ttl: int):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Проверка, истек ли срок жизни записи"""
        return time.time() - self.created_at > self.ttl


class InMemoryCache:
    """In-memory кеш с TTL"""
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._ttl = settings.cache_ttl
    
    def _generate_key(self, text: str, scenario: str) -> str:
        """Генерация ключа кеша на основе текста и сценария"""
        combined = f"{text}:{scenario}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, text: str, scenario: str) -> Optional[str]:
        """
        Получение значения из кеша
        
        Returns:
            Значение из кеша или None, если ключ не найден или истек
        """
        key = self._generate_key(text, scenario)
        
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            if entry.is_expired():
                del self._cache[key]
                return None
            
            return entry.value
    
    def set(self, text: str, scenario: str, value: str) -> None:
        """
        Сохранение значения в кеш
        """
        key = self._generate_key(text, scenario)
        
        with self._lock:
            self._cache[key] = CacheEntry(value, self._ttl)
    
    def clear(self) -> None:
        """Очистка кеша"""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кеша"""
        with self._lock:
            total = len(self._cache)
            expired = sum(1 for entry in self._cache.values() if entry.is_expired())
            
            return {
                "total_entries": total,
                "expired_entries": expired,
                "active_entries": total - expired
            }


# Глобальный экземпляр кеша
cache = InMemoryCache()