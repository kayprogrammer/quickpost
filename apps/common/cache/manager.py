from typing import Any, Optional, List
from django.core.cache import cache
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django_redis import get_redis_connection
import json, hashlib, logging
from django.forms.models import model_to_dict

logger = logging.getLogger(__name__)


class CacheManager:
    """Centralized cache management for Redis operations."""

    @staticmethod
    def _prepare_for_cache(value: Any) -> Any:
        """Convert Django models to serializable dicts."""
        # Early return for primitives (most common case)
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        
        if isinstance(value, Model):
            return CacheManager._model_to_dict(value)

        if isinstance(value, list):
            # Empty list - fast path
            if not value:
                return []
            
            # Check if all items are models (more robust than checking just first item)
            # Use a sample-based approach for large lists to avoid checking every item
            sample_size = min(len(value), 10)  # Check first 10 items
            sample_items = value[:sample_size]
            
            if all(isinstance(item, Model) for item in sample_items):
                # All sampled items are models, assume all are models
                # Use list comprehension (faster than map for small-medium lists)
                return [CacheManager._model_to_dict(item) for item in value]
            elif any(isinstance(item, Model) for item in sample_items):
                # Mixed types - need to check each item
                return [
                    CacheManager._model_to_dict(item) if isinstance(item, Model)
                    else CacheManager._prepare_for_cache(item)
                    for item in value
                ]
            else:
                # No models in sample - recursively prepare each item
                # But avoid recursion for primitives
                return [
                    item if isinstance(item, (str, int, float, bool, type(None)))
                    else CacheManager._prepare_for_cache(item)
                    for item in value
                ]

        if isinstance(value, tuple):
            # Special case for (status_code, response_data) pattern
            if len(value) == 2 and isinstance(value[1], dict):
                status_code, response_data = value
                response_data = response_data.copy()
                if "data" in response_data:
                    response_data["data"] = CacheManager._prepare_for_cache(
                        response_data["data"]
                    )
                return (status_code, response_data)
            # Generic tuple handling
            return tuple(
                item if isinstance(item, (str, int, float, bool, type(None)))
                else CacheManager._prepare_for_cache(item)
                for item in value
            )

        if isinstance(value, dict):
            # Optimize dict comprehension by avoiding recursion for primitives
            return {
                k: (v if isinstance(v, (str, int, float, bool, type(None)))
                    else CacheManager._prepare_for_cache(v))
                for k, v in value.items()
            }

        return value

    @staticmethod
    def _model_to_dict(instance: Model) -> dict:
        """Convert Django model instance to dictionary."""
        data = model_to_dict(instance)

        # Handle ID field
        if "id" not in data:
            data["id"] = str(instance.pk)
        else:
            data["id"] = str(data["id"])

        # Convert UUID fields to strings (more efficient than checking hasattr)
        # Only iterate if there are items to process
        if data:
            for key, value in list(data.items()):  # Use list() to avoid dict mutation issues
                if value is not None and hasattr(value, "hex"):
                    data[key] = str(value)

        return data

    @staticmethod
    def _hash_params(params: dict) -> str:
        """Create a consistent hash from parameters."""
        sorted_params = json.dumps(params, sort_keys=True, default=str)
        return hashlib.md5(sorted_params.encode()).hexdigest()

    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        try:
            redis_client = get_redis_connection("default")
            cached_json = redis_client.get(key)

            if cached_json is not None:
                value = json.loads(cached_json)
                return value

            return None
        except Exception as e:
            logger.error(f"Cache GET error for key '{key}': {e}")
            return None

    @staticmethod
    def set(key: str, value: Any, ttl: int = 300) -> bool:
        """Store value in cache."""
        try:
            prepared_value = CacheManager._prepare_for_cache(value)
            json_value = json.dumps(prepared_value, cls=DjangoJSONEncoder)

            redis_client = get_redis_connection("default")
            redis_client.setex(key, ttl, json_value)

            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache SET error for key '{key}': {e}")
            return False

    @staticmethod
    def delete(key: str) -> bool:
        """Delete a specific key from cache."""
        try:
            cache.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache DELETE error for key '{key}': {e}")
            return False

    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """Delete all keys matching a pattern."""
        try:
            redis_conn = get_redis_connection("default")
            keys = redis_conn.keys(pattern)

            if not keys:
                logger.debug(f"No keys found for pattern: {pattern}")
                return 0

            deleted_count = redis_conn.delete(*keys)
            logger.info(
                f"Cache INVALIDATE: {deleted_count} keys deleted for pattern '{pattern}'"
            )
            return deleted_count

        except ImportError:
            logger.warning(
                "django-redis not installed, using fallback pattern deletion"
            )
            cache.delete(pattern.replace("*", ""))
            return 1
        except Exception as e:
            logger.error(f"Cache DELETE_PATTERN error for pattern '{pattern}': {e}")
            return 0

    @staticmethod
    def clear_all() -> bool:
        """Clear all cache entries."""
        try:
            cache.clear()
            logger.warning("Cache CLEAR: All cache entries cleared")
            return True
        except Exception as e:
            logger.error(f"Cache CLEAR error: {e}")
            return False

    @staticmethod
    def build_key(
        key_template: str,
        context: dict,
        hash_params: Optional[List[str]] = None,
    ) -> str:
        """
        Build cache key from template and context.

        Args:
            key_template: Template with placeholders (e.g., 'user:{{user_id}}:profile')
            context: Dictionary with values to replace placeholders
            hash_params: List of parameter names to hash (e.g., ['filters', 'options'])

        Examples:
            >>> CacheManager.build_key('user:{{user_id}}:profile', {'user_id': 123})
            'user:123:profile'

            >>> CacheManager.build_key(
            ...     'posts:list:{{currency}}:{{filters}}',
            ...     {'currency': 'NGN', 'filters': {'active': True}},
            ...     hash_params=['filters']
            ... )
            'posts:list:NGN:a1b2c3d4'
        """
        resolved_key = key_template

        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in resolved_key:
                if hash_params and key in hash_params:
                    if isinstance(value, (dict, list)):
                        hashed_value = CacheManager._hash_params({key: value})
                        resolved_key = resolved_key.replace(placeholder, hashed_value)
                    else:
                        resolved_key = resolved_key.replace(placeholder, str(value))
                else:
                    resolved_key = resolved_key.replace(placeholder, str(value))

        cache_prefix = getattr(settings, "CACHE_KEY_PREFIX", "quickpost")
        return f"{cache_prefix}:{resolved_key}"

    @staticmethod
    def get_or_set(
        key: str,
        callback: callable,
        ttl: int = 300,
        *args,
        **kwargs,
    ) -> Any:
        """Get value from cache or compute and cache it."""
        cached_value = CacheManager.get(key)
        if cached_value is not None:
            return cached_value

        computed_value = callback(*args, **kwargs)
        CacheManager.set(key, computed_value, ttl)

        return computed_value
