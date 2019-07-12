from prometheus_client import (Counter, generate_latest,
                               CollectorRegistry, multiprocess)

# Prometheus Metrics
METRICS = {
    'processed_messages_total': Counter(
        'aiops_incoming_listener_processed_messages_total',
        'The total number of messages successfully processed'
    ),
}


def generate_aggregated_metrics():
    """Generate Aggregated Metrics for multiple processes."""
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return generate_latest(registry)
