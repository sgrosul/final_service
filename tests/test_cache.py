import time
import pytest
from cache.cache import InMemoryCache, cache


@pytest.fixture
def test_cache():
    """Фикстура для создания экземпляра кеша"""
    return InMemoryCache()


def test_cache_set_get(test_cache):
    """Тест сохранения и получения из кеша"""
    test_cache.set("test_text", "test_scenario", "test_value")
    result = test_cache.get("test_text", "test_scenario")
    assert result == "test_value"


def test_cache_miss(test_cache):
    """Тест промаха кеша"""
    result = test_cache.get("nonexistent", "scenario")
    assert result is None


def test_cache_ttl(test_cache):
    """Тест истечения TTL"""
    # Устанавливаем маленький TTL для теста
    test_cache._ttl = 1
    test_cache.set("test_text", "scenario", "value")
    
    # Ждем истечения TTL
    time.sleep(1.5)
    
    result = test_cache.get("test_text", "scenario")
    assert result is None


def test_cache_different_scenarios(test_cache):
    """Тест разных сценариев для одного текста"""
    test_cache.set("text", "scenario1", "value1")
    test_cache.set("text", "scenario2", "value2")
    
    result1 = test_cache.get("text", "scenario1")
    result2 = test_cache.get("text", "scenario2")
    
    assert result1 == "value1"
    assert result2 == "value2"
    assert result1 != result2


def test_cache_stats(test_cache):
    """Тест статистики кеша"""
    test_cache.set("text1", "scenario1", "value1")
    test_cache.set("text2", "scenario2", "value2")
    
    stats = test_cache.get_stats()
    assert stats["total_entries"] == 2
    assert stats["active_entries"] == 2


def test_cache_clear(test_cache):
    """Тест очистки кеша"""
    test_cache.set("text", "scenario", "value")
    test_cache.clear()
    
    result = test_cache.get("text", "scenario")
    assert result is None