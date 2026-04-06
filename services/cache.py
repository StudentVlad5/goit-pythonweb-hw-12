"""
Caching Service Module
----------------------
This module provides caching functionality using Redis to store and retrieve 
user data, reducing the number of direct database queries.
"""

import redis
import pickle
from config.config import settings

r = redis.Redis(
    host=settings.redis_host, 
    port=settings.redis_port, 
    db=0
)

def cache_user(user):
    """
        Serializes and stores a user object in the Redis cache.

        The user object is pickled and stored with a Time-To-Live (TTL) of 15 minutes.

        :param user: The User model instance to be cached.
        :type user: User
        :return: None
        """
    if user:
        # Секунди: 15 хвилин * 60
        r.setex(f"user:{user.email}", 900, pickle.dumps(user))

def get_cached_user(email: str):
    """
    Retrieves and deserializes a user object from the Redis cache.

    :param email: The email address of the user (used as the cache key).
    :type email: str
    :return: The User object if found in cache, otherwise None.
    :rtype: User | None
    """
    user_data = r.get(f"user:{email}")
    if user_data:
        return pickle.loads(user_data)
    return None