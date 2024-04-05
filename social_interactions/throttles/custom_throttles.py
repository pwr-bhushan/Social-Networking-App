from rest_framework.throttling import UserRateThrottle


class PerMinuteThrottle(UserRateThrottle):
    """
    Custom throttle class to limit requests per minute
    """

    scope = "per_minute"
