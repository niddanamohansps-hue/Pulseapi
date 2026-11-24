from pulseapi import PulseClient


def test_client_init():
    client = PulseClient(api_key="pk_live_test123", debug=True)
    assert client.api_key == "pk_live_test123"
    assert client.debug is True
    assert client.dropped_batches_count == 0


def test_client_send_failure_increments_drop_counter_without_raising():
    # Target an unreachable port
    client = PulseClient(
        api_key="pk_live_test123",
        endpoint_url="http://127.0.0.1:59999",
        debug=True,
        timeout=0.2,
    )
    success = client.send_batch("batch_test_001", {"requests": 42})

    # Must fail gracefully, return False, and increment dropped count
    assert success is False
    assert client.dropped_batches_count == 1

    # Second failure increments counter
    client.send_batch("batch_test_002", {"requests": 10})
    assert client.dropped_batches_count == 2
