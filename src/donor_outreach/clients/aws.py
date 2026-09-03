"""Shared boto3 session/client factory.

ONE shared AWS session for the entire app, built from a named CLI
profile rather than raw credentials — keys never pass through
Python config or .env, only the profile name does.
"""

from functools import lru_cache

import boto3

from donor_outreach.config import get_settings


@lru_cache(maxsize=1)
def get_session() -> boto3.Session:
    """Return the one shared boto3 Session for this app process."""
    settings = get_settings()
    return boto3.Session(profile_name=settings.aws_profile, region_name=settings.aws_region)


@lru_cache(maxsize=None)
def get_client(service_name: str):
    """Return a cached boto3 client for a given AWS service name."""
    return get_session().client(service_name)