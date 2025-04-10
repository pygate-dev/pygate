"""
The contents of this file are property of pygate.org
Review the Apache License 2.0 for valid authorization of use
See https://github.com/pypeople-dev/pygate for more information
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT

from services.subscription_service import SubscriptionService
from utils.auth_util import auth_required
from models.subscribe_model import SubscribeModel
from utils.group_util import group_required
from utils.response_util import process_response\

import uuid
import time
import logging

subscription_router = APIRouter()

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger("pygate.gateway")

@subscription_router.post("/subscribe",
    description="Subscribe to API",
    dependencies=[
        Depends(auth_required)
    ])
async def subscribe_api(api_data: SubscribeModel, request: Request, Authorize: AuthJWT = Depends()):
    request_id = str(uuid.uuid4())
    start_time = time.time() * 1000
    try:
        logger.info(f"{request_id} | Username: {Authorize.get_jwt_subject()} | From: {request.client.host}:{request.client.port}")
        logger.info(f"{request_id} | Endpoint: {request.method} {str(request.url.path)}")
        if not await group_required(None, Authorize, api_data.api_name + '/' + api_data.api_version):
            raise HTTPException(status_code=403, detail="You do not have the correct group access")
        return process_response(await SubscriptionService.subscribe(api_data, request_id))
    except ValueError as e:
        logger.error(f"{request_id} | Error: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": "Unable to process request"}, status_code=500)
    except Exception as e:
        logger.critical(f"{request_id} | Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": "An unexpected error occurred"}, status_code=500)
    finally:
        end_time = time.time() * 1000
        logger.info(f"{request_id} | Total time: {str(end_time - start_time)}ms")

@subscription_router.post("/unsubscribe",
    description="Unsubscribe from API",
    dependencies=[
        Depends(auth_required)
    ])
async def unsubscribe_api(api_data: SubscribeModel, request: Request, Authorize: AuthJWT = Depends()):
    request_id = str(uuid.uuid4())
    start_time = time.time() * 1000
    try:
        logger.info(f"{request_id} | Username: {Authorize.get_jwt_subject()} | From: {request.client.host}:{request.client.port}")
        logger.info(f"{request_id} | Endpoint: {request.method} {str(request.url.path)}")
        if not await group_required(None, Authorize, api_data.api_name + '/' + api_data.api_version):
            raise HTTPException(status_code=403, detail="You do not have the correct group access")
        return process_response(await SubscriptionService.unsubscribe(api_data, request_id))
    except ValueError as e:
        logger.error(f"{request_id} | Error: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": "Unable to process request"}, status_code=500)
    except Exception as e:
        logger.critical(f"{request_id} | Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": "An unexpected error occurred"}, status_code=500)
    finally:
        end_time = time.time() * 1000
        logger.info(f"{request_id} | Total time: {str(end_time - start_time)}ms")

@subscription_router.get("/subscriptions/{user_id}",
    description="Get user's subscriptions",
    dependencies=[
        Depends(auth_required)
    ])
async def subscriptions_for_user_by_id(user_id: str, request: Request, Authorize: AuthJWT = Depends()):
    request_id = str(uuid.uuid4())
    start_time = time.time() * 1000
    try:
        logger.info(f"{request_id} | Username: {Authorize.get_jwt_subject()} | From: {request.client.host}:{request.client.port}")
        logger.info(f"{request_id} | Endpoint: {request.method} {str(request.url.path)}")
        return process_response(await SubscriptionService.get_user_subscriptions(user_id, request_id))
    except ValueError as e:
        logger.error(f"{request_id} | Error: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": "Unable to process request"}, status_code=500)
    except Exception as e:
        logger.critical(f"{request_id} | Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": "An unexpected error occurred"}, status_code=500)
    finally:
        end_time = time.time() * 1000
        logger.info(f"{request_id} | Total time: {str(end_time - start_time)}ms")

@subscription_router.get("/subscriptions",
    description="Get current user's subscriptions",
    dependencies=[
        Depends(auth_required)
    ])
async def subscriptions_for_current_user(request: Request, Authorize: AuthJWT = Depends()):
    request_id = str(uuid.uuid4())
    start_time = time.time() * 1000
    try:
        logger.info(f"{request_id} | Username: {Authorize.get_jwt_subject()} | From: {request.client.host}:{request.client.port}")
        logger.info(f"{request_id} | Endpoint: {request.method} {str(request.url.path)}")
        username = Authorize.get_jwt_subject()
        return process_response(await SubscriptionService.get_user_subscriptions(username, request_id))
    except ValueError as e:
        logger.error(f"{request_id} | Error: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": "Unable to process request"}, status_code=500)
    except Exception as e:
        logger.critical(f"{request_id} | Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": "An unexpected error occurred"}, status_code=500)
    finally:
        end_time = time.time() * 1000
        logger.info(f"{request_id} | Total time: {str(end_time - start_time)}ms")