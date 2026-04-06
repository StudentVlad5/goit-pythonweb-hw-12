"""
Rate Limiter Service Module
---------------------------
This module initializes the rate limiting mechanism for the FastAPI application 
using the `slowapi` library. It helps prevent brute-force attacks and API abuse 
by restricting the number of requests from a single source.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

#: Instance of the Limiter. 
#: Uses the remote IP address of the client as the unique identifier for rate limits.
limiter = Limiter(key_func=get_remote_address)