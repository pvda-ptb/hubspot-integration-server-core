from celery import Task, shared_task
import redis

# Import the configuration to get the broker URL for our custom client.
from ..config import configuration

# Create the Redis client for our rate limiter from the same broker URL.
redis_client = redis.from_url(configuration['CELERY_BROKER_URL'], decode_responses=True)


def _parse_rate_limit(rate_limit_string):
    """Parses a rate limit string like '10/s', '600/m' into (calls, period_seconds)."""
    if not rate_limit_string:
        raise ValueError("Rate limit string cannot be empty.")

    parts = rate_limit_string.split('/')
    if len(parts) != 2:
        raise ValueError(f"Invalid rate limit format '{rate_limit_string}'. Use 'calls/period' (e.g., '10/s').")

    try:
        limit = int(parts[0])
    except (ValueError, TypeError):
        raise ValueError(f"Invalid call limit '{parts[0]}'. Must be an integer.")

    period_char = parts[1].lower()
    if period_char == 's':
        period_seconds = 1
    elif period_char == 'm':
        period_seconds = 60
    elif period_char == 'h':
        period_seconds = 3600
    else:
        raise ValueError(f"Invalid period '{parts[1]}'. Use 's', 'm', or 'h'.")

    return limit, period_seconds


class RateLimitedTask(Task):
    """
    This custom base Task implements the token bucket algorithm for API rate limiting.
    Rate limit values are parsed lazily on first call.
    """
    abstract = True

    # These attributes must be set on the subclass by the decorator.
    base_key_prefix = None
    rate_limit = None

    _rate_limit_calls = None
    _rate_limit_period = None
    _rate_limit_initialized = False

    def _initialize_rate_limit(self):
        """Parse the rate limit string and set the internal values."""
        if not self._rate_limit_initialized:
            if not hasattr(self, 'base_key_prefix') or self.base_key_prefix is None:
                raise NotImplementedError("Subclasses of RateLimitedTask must define a 'base_key_prefix'.")
            if self.rate_limit is None:
                raise ValueError("Task 'rate_limit' attribute cannot be None.")

            self._rate_limit_calls, self._rate_limit_period = _parse_rate_limit(self.rate_limit)
            self._rate_limit_initialized = True

    def __call__(self, *args, **kwargs):
        """
        This method is executed by the worker *before* the task's run() method.
        We inject the rate-limiting logic here.
        """
        self._initialize_rate_limit()

        # The first argument to the task is assumed to be the client_id for rate limiting.
        if not args:
            raise ValueError("RateLimitedTask requires a client_id as the first argument.")
        client_id = args[0]

        bucket_key = f"{self.base_key_prefix}:{self.name}:{client_id}"

        pipe = redis_client.pipeline()
        pipe.get(bucket_key)
        pipe.decr(bucket_key)
        tokens_before, tokens_after = pipe.execute()

        if tokens_before is None:
            # First call for this key, set the token bucket with a TTL.
            redis_client.setex(bucket_key, self._rate_limit_period, self._rate_limit_calls - 1)
            return super().__call__(*args, **kwargs)

        if tokens_after < 0:
            # Rate limit exceeded, increment back the token count and retry the task.
            redis_client.incr(bucket_key)
            self.retry(countdown=self._rate_limit_period)

        return super().__call__(*args, **kwargs)


def create_api_task_decorator(key_prefix, rate_limit_string):
    """
    A generic factory that creates a decorator for API tasks.

    :param key_prefix: The unique string to use for this API's Redis keys.
    :param rate_limit_string: The rate limit string (e.g., '10/s').
    """
    def wrapper(func):
        class CustomTask(RateLimitedTask):
            # Set the required class attributes on our dynamic task class
            base_key_prefix = key_prefix
            rate_limit = rate_limit_string

        return shared_task(base=CustomTask, bind=True)(func)
    return wrapper


# --- Create and export the specialized decorators ---

hubspot_task = create_api_task_decorator(
    key_prefix='hubspot',
    rate_limit_string=configuration['HUBSPOT_RATE_LIMIT'],
)
