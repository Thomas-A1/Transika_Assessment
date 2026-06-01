"""
Helper functions for time and ids.
"""

import uuid
from datetime import datetime, timezone


def now_utc():
    return datetime.now(timezone.utc)


def iso(dt):
    """Format a datetime as an ISO string ending in 'Z'."""
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def new_id(prefix):
    return prefix + "_" + uuid.uuid4().hex
