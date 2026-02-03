from redis import Redis

DAILY_LIMIT = 5
TTL_SECONDS = 60 * 60 * 24  # 24시간

def get_redis() -> Redis:
    """
    배포에서는 환경변수(REDIS_URL)로 넣는 걸 추천.
    예: redis://:password@host:6379/0
    """
    import os
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return Redis.from_url(url, decode_responses=True)

_LUA = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""

def consume_24h(username: str) -> tuple[bool, int]:
    """
    username 기준으로 '첫 사용 시점부터 24시간' 동안 5회 제한
    return: (allowed, remaining)
    """
    r = get_redis()
    key = f"chat_limit_24h:{username}"

    used = int(r.eval(_LUA, 1, key, TTL_SECONDS))  # 1회 차감까지 포함된 값
    remaining = DAILY_LIMIT - used

    if used > DAILY_LIMIT:
        return False, 0
    return True, max(0, remaining)

def get_remaining_24h(username: str) -> int:
    """
    현재 남은 횟수(대략) 조회용. (정확한 차감은 consume_24h로)
    """
    r = get_redis()
    key = f"chat_limit_24h:{username}"
    used = r.get(key)
    used = int(used) if used is not None else 0
    return max(0, DAILY_LIMIT - used)
