import os
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter


# Custom session class that supports both caching and rate limiting
class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


# Initialize session
session = CachedLimiterSession(
    limiter=Limiter(RequestRate(3, Duration.SECOND * 5)),
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache(os.path.join(os.getcwd(), r".cache\yfinance")),
    expire_after=60 * 60,
)
