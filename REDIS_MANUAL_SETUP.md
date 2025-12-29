# Manual Redis Configuration (Without Docker)

If you prefer to run Redis locally on your machine instead of using Docker, here's how to set it up for different operating systems.

## macOS Installation

### Using Homebrew (Recommended)

```bash
# Install Redis
brew install redis

# Start Redis as a background service
brew services start redis

# Or run Redis manually (stops when terminal closes)
redis-server

# Check if Redis is running
redis-cli ping
# Should return: PONG
```

### Configuration

Redis config file location: `/opt/homebrew/etc/redis.conf` (Apple Silicon) or `/usr/local/etc/redis.conf` (Intel)

```bash
# Edit the config file
nano /opt/homebrew/etc/redis.conf

# Key settings to check:
# port 6379
# bind 127.0.0.1
# maxmemory 256mb
# maxmemory-policy allkeys-lru
```

Restart Redis after config changes:
```bash
brew services restart redis
```

---

## Linux (Ubuntu/Debian) Installation

```bash
# Update package list
sudo apt update

# Install Redis
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server

# Enable Redis to start on boot
sudo systemctl enable redis-server

# Check status
sudo systemctl status redis-server

# Test connection
redis-cli ping
# Should return: PONG
```

### Configuration

Edit the config file:
```bash
sudo nano /etc/redis/redis.conf
```

Important settings:
```conf
# Listen on localhost only (secure)
bind 127.0.0.1

# Port
port 6379

# Memory limit
maxmemory 256mb

# Eviction policy (remove least recently used keys when memory is full)
maxmemory-policy allkeys-lru

# Enable persistence (optional - saves data to disk)
save 900 1      # Save if 1 key changed in 900 seconds
save 300 10     # Save if 10 keys changed in 300 seconds
save 60 10000   # Save if 10000 keys changed in 60 seconds
```

Restart after changes:
```bash
sudo systemctl restart redis-server
```

---

## Windows Installation

### Using WSL2 (Recommended)

If you're on Windows 10/11, use WSL2 with Ubuntu and follow the Linux instructions above.

### Native Windows (Using Memurai)

Redis doesn't officially support Windows, but Memurai is a Redis-compatible alternative:

1. Download Memurai from https://www.memurai.com/
2. Install and run as a Windows service
3. Default port: 6379

Or use Redis from Microsoft's archive:
```powershell
# Download from GitHub
# https://github.com/microsoftarchive/redis/releases

# Extract and run
redis-server.exe
```

---

## Verifying Your Installation

Once Redis is running, test it:

```bash
# Connect to Redis CLI
redis-cli

# Inside Redis CLI:
127.0.0.1:6379> ping
PONG

127.0.0.1:6379> set test "Hello Redis"
OK

127.0.0.1:6379> get test
"Hello Redis"

127.0.0.1:6379> del test
(integer) 1

127.0.0.1:6379> exit
```

---

## Django Configuration for Local Redis

Update your `.env` file:

```env
# For local Redis (default)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

Your `settings/base.py` already handles this:

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{config('REDIS_HOST', default='127.0.0.1')}:{config('REDIS_PORT', default='6379')}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "quickpost",
        "TIMEOUT": 300,
    }
}
```

---

## Useful Redis Commands

### Monitoring

```bash
# Monitor all commands in real-time
redis-cli monitor

# Get server info
redis-cli info

# Check memory usage
redis-cli info memory

# See connected clients
redis-cli client list
```

### Managing Keys

```bash
# List all keys
redis-cli keys "*"

# List keys with pattern
redis-cli keys "quickpost:posts:*"

# Count total keys
redis-cli dbsize

# Get key type
redis-cli type "quickpost:posts:list:anon"

# Check TTL (time to live)
redis-cli ttl "quickpost:posts:list:anon"

# Delete a key
redis-cli del "quickpost:posts:list:anon"

# Delete all keys (DANGEROUS!)
redis-cli flushall
```

### Performance Testing

```bash
# Benchmark Redis performance
redis-benchmark -q -n 10000

# Test specific operations
redis-benchmark -t set,get -n 100000 -q
```

---

## Troubleshooting

### Redis Won't Start

**Check if port 6379 is already in use:**
```bash
# macOS/Linux
lsof -i :6379

# Kill the process if needed
kill -9 <PID>
```

**Check Redis logs:**
```bash
# macOS (Homebrew)
tail -f /opt/homebrew/var/log/redis.log

# Linux
sudo tail -f /var/log/redis/redis-server.log
```

### Connection Refused

Make sure Redis is running:
```bash
# macOS
brew services list | grep redis

# Linux
sudo systemctl status redis-server
```

Check if it's listening on the right port:
```bash
netstat -an | grep 6379
```

### Permission Denied

On Linux, Redis might need proper permissions:
```bash
sudo chown redis:redis /var/lib/redis
sudo chmod 755 /var/lib/redis
```

---

## Security Best Practices

### 1. Bind to Localhost Only

In `redis.conf`:
```conf
bind 127.0.0.1 ::1
```

This prevents external connections. Only your local machine can access Redis.

### 2. Set a Password (Optional for Development)

```conf
requirepass your_strong_password_here
```

Update Django settings:
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://:{config('REDIS_PASSWORD')}@{config('REDIS_HOST')}:6379/1",
        # ...
    }
}
```

### 3. Disable Dangerous Commands

```conf
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

---

## Development vs Production

### Development Setup (What We're Using)

```conf
bind 127.0.0.1
port 6379
maxmemory 256mb
maxmemory-policy allkeys-lru
# No password needed for local dev
```

### Production Setup (For Later)

```conf
bind 0.0.0.0  # Or specific IP
port 6379
requirepass strong_password_here
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

---

## Stopping Redis

### macOS
```bash
# If running as service
brew services stop redis

# If running manually
# Just Ctrl+C in the terminal
```

### Linux
```bash
sudo systemctl stop redis-server

# Or
sudo service redis-server stop
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Start Redis | `brew services start redis` (macOS)<br>`sudo systemctl start redis-server` (Linux) |
| Stop Redis | `brew services stop redis` (macOS)<br>`sudo systemctl stop redis-server` (Linux) |
| Restart Redis | `brew services restart redis` (macOS)<br>`sudo systemctl restart redis-server` (Linux) |
| Test connection | `redis-cli ping` |
| View all keys | `redis-cli keys "*"` |
| Clear all cache | `redis-cli flushall` |
| Monitor activity | `redis-cli monitor` |
| Check memory | `redis-cli info memory` |

---

## Next Steps

Once Redis is running locally:

1. ✅ Verify connection: `redis-cli ping`
2. ✅ Update `.env` with Redis host/port
3. ✅ Install Python packages: `pip install django-redis hiredis`
4. ✅ Run your Django app: `make run`
5. ✅ Test caching by making API requests

You're all set! Redis is now running on your local machine and ready to cache your API responses.
