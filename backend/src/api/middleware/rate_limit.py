from __future__ import annotations

import time
from collections import deque
from threading import Lock
from typing import Deque, Dict, Optional

# In-memory sliding window rate limiter.
# Keyed by a provided key (e.g., scope:user_id:client_ip).
# Suitable for single-process dev/test usage.


_STORE: Dict[str, Deque[float]] = {}
_LOCK: Lock = Lock()


def _now() -> float:
    return time.monotonic()


def check_rate_limit(key: str, limit: int, window_seconds: int) -> bool:
    """
    Return True if the request is allowed (under the limit), False if rate limited.
    Sliding window based on monotonic time for stability in tests.
    """
    now = _now()
    cutoff = now - window_seconds

    with _LOCK:
        q = _STORE.get(key)
        if q is None:
            q = deque()
            _STORE[key] = q

        # Prune old timestamps outside the window
        while q and q[0] < cutoff:
            q.popleft()

        # Enforce limit
        if len(q) >= limit:
            return False

        # Record this request
        q.append(now)
        return True


def make_rate_limit_key(scope: str, *, user_id: Optional[str] = None, client_ip: Optional[str] = None) -> str:
    """
    Construct a consistent limiter key. Prefer user_id scoping; fall back to client_ip.
    """
    uid = user_id or "-"
    ip = client_ip or "-"
    return f"{scope}:{uid}:{ip}"


def reset_rate_limiter() -> None:
    """
    Clear limiter state (useful in tests).
    """
    with _LOCK:
        _STORE.clear()
