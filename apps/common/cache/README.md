# QuickPost Cache System

A sophisticated Redis-based caching mechanism for Django Ninja with decorator-based API.

## Features

- **Template-based cache keys** with placeholder syntax
- **Automatic parameter hashing** for complex objects
- **Pattern-based invalidation** with wildcard support
- **Async and sync function support**
- **Debug mode** for development
- **Context-aware** caching (works seamlessly with Django Ninja)

## Installation

Install Redis dependencies:

```bash
pip install django-redis hiredis
```

## Configuration

In your `settings/base.py`:

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",
        },
        "KEY_PREFIX": "quickpost",
        "TIMEOUT": 300,
    }
}

CACHE_KEY_PREFIX = "quickpost"
```

## Quick Start

### 1. Basic Caching

```python
from apps.common.cache import cacheable

@cacheable(
    key='posts:{{slug}}',
    ttl=600  # 10 minutes
)
async def get_post(request, slug: str):
    post = await Post.objects.select_related('author').aget(slug=slug)
    return post
```

**Generated cache key**: `quickpost:posts:my-post-slug`

### 2. Caching with User Context

```python
@cacheable(
    key='profiles:{{user_id}}',
    ttl=300,
    debug=True
)
async def get_user_profile(request):
    # user_id is automatically extracted from request.auth
    user = request.auth
    return user
```

**Generated key**: `quickpost:profiles:123e4567-...`

### 3. Cache Invalidation

```python
from apps.common.cache import invalidate_cache

@invalidate_cache(
    patterns=[
        'posts:{{slug}}:*',
        'posts:list:*',
    ]
)
async def update_post(request, slug: str, data: dict):
    post = await Post.objects.aget(slug=slug)
    for key, value in data.items():
        setattr(post, key, value)
    await post.asave()
    return post
```

### 4. Manual Cache Operations

```python
from apps.common.cache import CacheManager

# Get from cache
value = CacheManager.get('posts:my-slug')

# Set cache with TTL
CacheManager.set('posts:my-slug', post_data, ttl=600)

# Delete specific key
CacheManager.delete('posts:my-slug')

# Delete by pattern
CacheManager.delete_pattern('posts:*')

# Get or compute
def fetch_post():
    return Post.objects.get(slug='my-slug')

post = CacheManager.get_or_set('posts:my-slug', fetch_post, ttl=600)
```

## Real-World Examples

### Example 1: Blog Posts List

```python
from apps.common.cache import cacheable, invalidate_cache

# Cache posts list with filters
@cacheable(
    key='posts:list:{{user_id}}',
    ttl=300  # 5 minutes
)
async def get_posts(request, filters: PostFilterSchema = Query(...)):
    # Query params are automatically hashed
    query = Post.objects.filter(deleted_at__isnull=True)
    
    if filters.author_id:
        query = query.filter(author_id=filters.author_id)
    
    posts = await query.select_related('author').all()
    return list(posts)


# Invalidate when creating posts
@invalidate_cache(patterns=['posts:list:*'])
async def create_post(request, data: PostCreateSchema):
    post = await Post.objects.acreate(author=request.auth, **data.dict())
    return post


# Invalidate specific post and all lists
@invalidate_cache(patterns=[
    'posts:{{slug}}:*',
    'posts:list:*'
])
async def update_post(request, slug: str, data: PostCreateSchema):
    post = await Post.objects.aget(slug=slug)
    for key, value in data.dict(exclude_unset=True).items():
        setattr(post, key, value)
    await post.asave()
    return post
```

### Example 2: Comments System

```python
# Cache comments for a post
@cacheable(
    key='comments:post:{{slug}}:{{user_id}}',
    ttl=120  # 2 minutes - comments change frequently
)
async def get_comments(request, slug: str, sort: str = 'asc'):
    post = await Post.objects.aget(slug=slug)
    query = Comment.objects.filter(post=post, parent__isnull=True)
    
    if sort == 'desc':
        query = query.order_by('-created_at')
    else:
        query = query.order_by('created_at')
    
    comments = await query.select_related('author').all()
    return list(comments)


# Invalidate on comment creation
@invalidate_cache(
    patterns=[
        'comments:post:{{slug}}:*',
        'posts:{{slug}}:*',  # Also invalidate post detail (comment count may change)
    ]
)
async def create_comment(request, slug: str, data: CommentCreateSchema):
    post = await Post.objects.aget(slug=slug)
    comment = await Comment.objects.acreate(
        post=post,
        author=request.auth,
        text=data.text
    )
    return comment
```

### Example 3: User Profile

```python
# Cache user profile
@cacheable(
    key='profiles:{{user_id}}',
    ttl=600  # 10 minutes
)
async def get_user_profile(request):
    user = request.auth
    return {
        'id': str(user.id),
        'full_name': user.full_name,
        'email': user.email,
        'avatar_url': user.avatar_url,
        'bio': user.bio,
    }


# Invalidate on profile update
@invalidate_cache(patterns=['profiles:{{user_id}}'])
async def update_profile(request, data: UserUpdateSchema):
    user = request.auth
    for key, value in data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    await user.asave()
    return user
```

### Example 4: Likes/Dislikes

```python
# Cache likes for a post
@cacheable(
    key='likes:post:{{obj_id}}:{{is_dislike}}',
    ttl=60  # 1 minute
)
async def get_likes(request, obj_id: UUID, is_dislike: bool = False):
    likes = await Like.objects.filter(
        post_id=obj_id,
        is_disliked=is_dislike
    ).select_related('author').all()
    
    return [
        {
            'id': str(like.id),
            'author': like.author.full_name,
            'created_at': like.created_at.isoformat(),
        }
        for like in likes
    ]


# Invalidate on like toggle
@invalidate_cache(
    patterns=[
        'likes:post:{{obj_id}}:*',
        'posts:{{obj_id}}:*',  # Post detail may show like count
    ]
)
async def toggle_like(request, obj_id: UUID, is_dislike: bool = False):
    like, created = await Like.objects.aget_or_create(
        post_id=obj_id,
        author=request.auth,
        defaults={'is_disliked': is_dislike}
    )
    
    if not created:
        await like.adelete()
    
    return {'liked': created}
```

## Cache Key Best Practices

### Good Patterns

✅ **Hierarchical structure**: `resource:id:subresource`
```python
key='posts:{{slug}}'
key='comments:post:{{slug}}'
key='likes:post:{{post_id}}'
```

✅ **Wildcard invalidation**: `resource:id:*`
```python
patterns=['posts:{{slug}}:*']      # Clear all post caches
patterns=['comments:post:{{slug}}:*']  # Clear all comment caches
```

✅ **Include context**: Separate by user
```python
key='posts:list:{{user_id}}'
key='profiles:{{user_id}}'
```

### Avoid

❌ Flat keys without hierarchy
```python
key='post_{{slug}}'  # Hard to manage
```

❌ Missing context (cache collision risk)
```python
key='profile'  # Collides across all users!
```

## TTL Guidelines

| Data Type | Suggested TTL | Example |
|-----------|---------------|---------|
| Static data | 1-24 hours | Post content, user profiles |
| User-specific | 5-15 minutes | User posts, comments |
| Frequently updated | 1-5 minutes | Like counts, comment counts |
| Real-time | 30-60 seconds | Notifications, live updates |

## Debug Mode

Enable debug logging to see cache operations:

```python
@cacheable(
    key='posts:{{slug}}',
    ttl=600,
    debug=True  # Enable debug logging
)
async def get_post(request, slug: str):
    return post
```

**Debug output**:
```
[Cache] get_post | Path: {'slug': 'my-post', 'user_id': 'anon'} | Query:  | Key: quickpost:posts:my-post
[Cache] MISS: quickpost:posts:my-post
[Cache] SET: quickpost:posts:my-post (TTL: 600s)
```

## Monitoring Cache

### Using Redis CLI

```bash
# Access Redis
docker-compose exec redis redis-cli

# List all QuickPost cache keys
KEYS quickpost:*

# Get specific value
GET quickpost:posts:my-post

# Check TTL remaining
TTL quickpost:posts:my-post

# Count keys by pattern
KEYS quickpost:posts:*

# Delete keys
DEL quickpost:posts:my-post
```

### Using Python

```python
from django_redis import get_redis_connection

redis_conn = get_redis_connection("default")

# Count keys by pattern
post_cache_count = len(redis_conn.keys('quickpost:posts:*'))

# Get memory usage
memory_info = redis_conn.info('memory')
print(f"Used memory: {memory_info['used_memory_human']}")
```

## Testing

```python
from apps.common.cache import CacheManager
import pytest

@pytest.mark.asyncio
async def test_get_post_caching():
    # Clear cache before test
    CacheManager.delete('quickpost:posts:test-slug')

    # First call - cache miss, queries database
    result1 = await get_post(request, slug='test-slug')

    # Second call - cache hit, no database query
    result2 = await get_post(request, slug='test-slug')

    assert result1 == result2

    # Verify cached
    cached = CacheManager.get('quickpost:posts:test-slug')
    assert cached is not None
```

## Performance Tips

1. **Cache expensive queries** - Database joins, aggregations
2. **Use appropriate TTLs** - Balance freshness vs performance
3. **Invalidate precisely** - Use specific patterns instead of wildcards when possible
4. **Monitor hit rates** - Check if caching is effective
5. **Avoid over-caching** - Only cache expensive operations

## Common Pitfalls

1. **Forgetting to invalidate** - Always add `@invalidate_cache` to mutations
2. **Cache stampede** - Multiple simultaneous requests on cache miss
3. **Stale data** - TTL too long for frequently updated data
4. **Over-caching** - Caching everything wastes memory

## Architecture

```
apps/common/cache/
├── __init__.py          # Public exports (cacheable, invalidate_cache, CacheManager)
├── manager.py           # CacheManager class (low-level operations)
├── decorators.py        # @cacheable and @invalidate_cache decorators
└── README.md            # This documentation
```

## Further Reading

- [Django Cache Framework](https://docs.djangoproject.com/en/5.2/topics/cache/)
- [django-redis Documentation](https://github.com/jazzband/django-redis)
- [Redis Documentation](https://redis.io/docs/)
