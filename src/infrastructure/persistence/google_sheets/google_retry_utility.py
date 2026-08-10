# infrastructure/google/google_retry_utility.py

import random
from time import sleep
from typing import Callable, TypeVar, Optional

from googleapiclient.errors import HttpError

T = TypeVar("T")


def retry_google_api_operation(
    operation: Callable[[], T],
    *,
    max_retries: int = 5,
    initial_delay_s: float = 1.0,
    max_delay_s: float = 32.0,
    on_retry: Optional[Callable[[int, float, HttpError], None]] = None,
) -> T:
    """
    Retry a Google API operation (Sheets, Drive, etc.) on transient errors
    using exponential backoff with jitter.

    :param operation: Zero-argument callable executing a Google API request.
    :param max_retries: Maximum number of attempts.
    :param initial_delay_s: Initial backoff delay in seconds.
    :param max_delay_s: Maximum backoff delay in seconds.
    :param on_retry: Optional callback invoked before each retry:
                     (attempt_number, delay_seconds, error)
    :raises HttpError: if retries are exhausted or error is non-transient
    :return: Operation result if successful.
    """

    delay = initial_delay_s

    for attempt in range(1, max_retries + 1):
        try:
            return operation()

        except HttpError as err:
            status = getattr(err.resp, "status", None)
            message = str(err)

            transient = (
                status in (429, 500, 502, 503, 504)
                or (status == 403 and "rateLimitExceeded" in message)
                or (status == 403 and "userRateLimitExceeded" in message)
            )

            if not transient or attempt == max_retries:
                raise

            # Add jitter to avoid thundering herd
            jitter = random.uniform(0.5, 1.5)
            sleep_time = min(delay * jitter, max_delay_s)

            if on_retry:
                on_retry(attempt, sleep_time, err)

            sleep(sleep_time)
            delay *= 2
