import json
import logging
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger("pulseapi")


class PulseClient:
    """
    PulseAPI Ingestion Client.
    Reliable buffer & dispatch client with drop-count tracking (Phase 0 Review Fix 6).
    Never raises an uncaught exception into the host application.
    """

    def __init__(
        self,
        api_key: str,
        endpoint_url: str = "http://localhost:8000",
        debug: bool = False,
        timeout: float = 3.0,
    ):
        self.api_key = api_key
        self.endpoint_url = endpoint_url.rstrip("/")
        self.debug = debug
        self.timeout = timeout
        self.dropped_batches_count = 0

    def send_batch(self, batch_id: str, data: dict[str, Any]) -> bool:
        """
        Sends an aggregated minute telemetry batch to PulseAPI ingestion endpoint.
        Returns True on success, False on failure.
        Never raises exceptions to caller.
        """
        url = f"{self.endpoint_url}/v1/ingest"
        payload = {
            "batch_id": batch_id,
            "dropped_previous_batches": self.dropped_batches_count,
            "data": data,
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": "pulseapi-python/0.1.0",
                    "X-PulseAPI-Dropped-Batches": str(self.dropped_batches_count),
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if 200 <= response.status < 300:
                    # Reset dropped counter on successful delivery
                    self.dropped_batches_count = 0
                    if self.debug:
                        logger.debug("PulseAPI: batch %s sent successfully", batch_id)
                    return True
                else:
                    self._record_drop(f"HTTP {response.status}")
                    return False

        except Exception as exc:
            self._record_drop(str(exc))
            return False

    def _record_drop(self, reason: str) -> None:
        """Internal helper to safely log and increment dropped batch count without raising."""
        self.dropped_batches_count += 1
        if self.debug:
            logger.debug(
                "PulseAPI: failed to deliver batch (total dropped: %d). Reason: %s",
                self.dropped_batches_count,
                reason,
            )
