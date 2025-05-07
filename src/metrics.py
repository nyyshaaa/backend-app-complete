from prometheus_client import Histogram

DB_LATENCY = Histogram(
    "frosty_prod_db_latency_seconds",
    "Time spent loading from the database",
    labelnames=["endpoint"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5),
)

SERIALIZE_LATENCY = Histogram(
    "frosty_prod_serialize_latency_seconds",
    "Time spent serializing the response",
    labelnames=["endpoint"],
    buckets=(0.0005, 0.001, 0.005, 0.01, 0.05),
)
