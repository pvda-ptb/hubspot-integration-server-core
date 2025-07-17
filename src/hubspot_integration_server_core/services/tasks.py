from celery import Task, shared_task
import redis

# Import the configuration to get the broker URL for our custom client.
from ..config import configuration

# Create the Redis client for our rate limiter from the same broker URL.
# redis.from_url() is the standard way to create a client from a URL string.
# We ensure decode_responses=True for convenient string handling.
redis_client = redis.from_url(configuration['CELERY_BROKER_URL'], decode_responses=True)


class RateLimitedTask(Task):
    """
    This custom base Task implements the token bucket algorithm for HubSpot API
    rate limiting. It now parses rate limit strings.
    """
    abstract = True

    # Default rate limit string. Can be overridden in subclasses or by the decorator.
    rate_limit = configuration.get('DEFAULT_RATE_LIMIT', None)

    def __init__(self):
        """On task initialization, parse the rate limit string."""
        super().__init__()
        if not hasattr(self, 'base_key_prefix'):
            raise NotImplementedError("Subclasses of RateLimitedTask must define a 'base_key_prefix'.")
        self._rate_limit_calls, self._rate_limit_period = self._parse_rate_limit(self.rate_limit)

    def _parse_rate_limit(self, rate_limit_string):
        """Parses a rate limit string like '10/s', '600/m' into (calls, period_seconds)."""
        if not rate_limit_string:
            raise ValueError("Rate limit string cannot be empty.")

        parts = rate_limit_string.split('/')
        if len(parts) != 2:
            raise ValueError(f"Invalid rate limit format '{rate_limit_string}'. Use 'calls/period' (e.g., '10/s').")

        try:
            limit = int(parts[0])
        except ValueError:
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

    def __call__(self, client_id, *args, **kwargs):
        """
        This method is executed by the worker *before* the task's run() method.
        We inject the rate-limiting logic here using the parsed values.
        """
        bucket_key = f"{self.base_key_prefix}:{self.name}:{client_id}"

        pipe = redis_client.pipeline()
        pipe.get(bucket_key)
        pipe.decr(bucket_key)
        tokens_before, tokens_after = pipe.execute()

        if tokens_before is None:
            redis_client.setex(bucket_key, self._rate_limit_period, self._rate_limit_calls - 1)
            return super().__call__(client_id, *args, **kwargs)

        if tokens_after < 0:
            redis_client.incr(bucket_key)
            self.retry(countdown=self._rate_limit_period)

        return super().__call__(client_id, *args, **kwargs)


def create_api_task_decorator(key_prefix, default_rate_limit):
    """
    A generic factory that creates a specialized decorator for any API client.

    :param key_prefix: The unique string to use for this API's Redis keys.
    :param default_rate_limit: The default rate limit string (e.g., '10/s').
    """

    def decorator(override_rate_limit=None):
        """
        The actual decorator. It can take an optional rate limit to override the default.
        :param override_rate_limit: An optional rate limit string (e.g., '10/s').
        """

        def wrapper(func):
            class CustomTask(RateLimitedTask):
                # Set the required class attributes on our dynamic task class
                base_key_prefix = key_prefix
                rate_limit = override_rate_limit if override_rate_limit is not None else default_rate_limit

            return shared_task(base=CustomTask, bind=True)(func)

        return wrapper

    return decorator


# --- Create and export the specialized decorators with a simple one-line call ---

hubspot_task = create_api_task_decorator(
    key_prefix='hubspot',
    default_rate_limit=configuration['HUBSPOT_RATE_LIMIT'],
)
