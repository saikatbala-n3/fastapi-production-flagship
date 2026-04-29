from prometheus_client import Counter, Histogram

http_requests = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)
http_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)
cache_hits = Counter("cache_hits_total", "Cache hits", ["operation"])
cache_misses = Counter("cache_misses_total", "Cache misses", ["operation"])
rate_limit_decisions = Counter(
    "rate_limit_decisions_total", "Rate limiter decisions", ["decisions"]
)
