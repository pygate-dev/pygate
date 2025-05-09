"""
The contents of this file are property of doorman.so
Review the Apache License 2.0 for valid authorization of use
See https://github.com/pypeople-dev/doorman for more information
"""

from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import MissingTokenError
from utils.doorman_cache_util import doorman_cache
from utils.database import subscriptions_collection

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger("doorman.gateway")

def subscription_required(request: Request, Authorize: AuthJWT = Depends()):
    try:
        username = Authorize.get_jwt_subject()
        full_path = request.url.path
        if full_path.startswith("/api/rest/"):
            prefix = "/api/rest/"
        elif full_path.startswith("/api/soap/"):
            prefix = "/api/soap/"
        else:
            prefix = ""
        if full_path.startswith(prefix):
            path = full_path[len(prefix):]
        else:
            path = full_path
        api_and_version = '/'.join(path.split('/')[:2])
        user_subscriptions = doorman_cache.get_cache('user_subscription_cache', username) or subscriptions_collection.find_one({'username': username})
        subscriptions = user_subscriptions.get('apis') if user_subscriptions and 'apis' in user_subscriptions else None
        if not subscriptions or api_and_version not in subscriptions:
            logger.info(f"User {username} attempted access to {api_and_version}")
            raise HTTPException(status_code=403, detail="You are not subscribed to this resource")
    except MissingTokenError:
        raise HTTPException(status_code=401, detail="Missing token")
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    return Authorize