import hashlib

from fastapi import HTTPException, Request

_INCREMENT = """
local count = redis.call("INCR", KEYS[1])
if count == 1 then redis.call("EXPIRE", KEYS[1], ARGV[1]) end
return count
"""


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def opaque(value: str) -> str:
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()


async def enforce(
    request: Request,
    scope: str,
    identity: str,
    limit: int,
    window_seconds: int = 60,
) -> None:
    key = f"rate-limit:{scope}:{identity}"
    count = await request.app.state.redis.eval(_INCREMENT, 1, key, window_seconds)
    if int(count) > limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={"Retry-After": str(window_seconds)},
        )
