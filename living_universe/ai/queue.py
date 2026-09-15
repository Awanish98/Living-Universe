"""Thread-safe queues for asynchronous AI observation requests and command dispatch."""

from queue import Queue
from typing import List, Optional, Any
from .base import AIResponse
from ..core.commands import WorldCommand


class AICommandQueue:
    """Thread-safe bidirectional queue for AI worker tasks and responses."""

    def __init__(self):
        self._request_queue = Queue()
        self._response_queue = Queue()

    def submit_request(self, request_type: str, payload: dict) -> None:
        """Submit a background request ('analyze' or 'command')."""
        self._request_queue.put((request_type, payload))

    def get_pending_request(self, timeout: Optional[float] = None) -> Optional[tuple]:
        if self._request_queue.empty():
            return None
        return self._request_queue.get(timeout=timeout)

    def post_response(self, response: AIResponse) -> None:
        """Post a completed AI response."""
        self._response_queue.put(response)

    def drain_responses(self) -> List[AIResponse]:
        """Fetch all completed responses without blocking."""
        results = []
        while not self._response_queue.empty():
            results.append(self._response_queue.get_nowait())
        return results
