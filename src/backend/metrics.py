from prometheus_client import Counter, Histogram, Gauge

# -----------------------------------
# Request metrics
# -----------------------------------

# request counter
REQUEST_COUNT = Counter(
    "appetite_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],   # EXACT LABELS
)

# latency histogram
REQUEST_LATENCY = Histogram(
    "appetite_request_latency_seconds",
    "Latency of HTTP requests in seconds",
    ["endpoint"],   # ONLY ONE LABEL
)

# in-progress requests
IN_PROGRESS = Gauge(
    "appetite_inprogress_requests",
    "Number of in-progress HTTP requests",
)

# -----------------------------------
# Feature usage metrics
# -----------------------------------
USAGE_COUNT = Counter(
    "appetite_feature_usage_total",
    "Count of feature usage",
    ["feature"],
)

# -----------------------------------
# Feedback metrics
# -----------------------------------
FEEDBACK_COUNT = Counter(
    "appetite_feedback_total",
    "User feedback count by page and rating",
    ["page", "rating"],
)