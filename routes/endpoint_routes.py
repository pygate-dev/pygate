"""
The contents of this file are property of pygate.org
Review the Apache License 2.0 for valid authorization of use
See https://github.com/pypeople-dev/pygate for more information
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT

from models.update_endpoint_model import UpdateEndpointModel
from services.endpoint_service import EndpointService
from utils.auth_util import auth_required
from models.endpoint_model import EndpointModel
from utils.response_util import process_response
from utils.role_util import platform_role_required_bool

endpoint_router = APIRouter()

"""
Create endpoint *platform endpoint.
"""
@endpoint_router.post("",
    dependencies=[
        Depends(auth_required)
    ])
async def create_endpoint(endpoint_data: EndpointModel, Authorize: AuthJWT = Depends()):
    try:
        if not await platform_role_required_bool(Authorize.get_jwt_subject(), 'manage_endpoints'):
            return JSONResponse(content={"error": "You do not have permission to create endpoints"}, status_code=403)
        return process_response(await EndpointService.create_endpoint(endpoint_data))
    except ValueError as e:
        return JSONResponse(content={"error": "Unable to process request"}, status_code=500)

"""
Update endpoint *platform endpoint.
""" 
@endpoint_router.put("/{endpoint_method}/{api_name}/{api_version}/{endpoint_uri}",
    dependencies=[
        Depends(auth_required)
    ])
async def update_endpoint(endpoint_method: str, api_name: str, api_version: str, endpoint_uri: str, endpoint_data: UpdateEndpointModel, Authorize: AuthJWT = Depends()):
    try:
        if not await platform_role_required_bool(Authorize.get_jwt_subject(), 'manage_endpoints'):
            return JSONResponse(content={"error": "You do not have permission to update endpoints"}, status_code=403)
        return process_response(await EndpointService.update_endpoint(endpoint_method, api_name, api_version, '/' + endpoint_uri, endpoint_data))
    except ValueError as e:
        return JSONResponse(content={"error": "Unable to process request"}, status_code=500)

"""
Delete endpoint *platform endpoint.
"""
@endpoint_router.delete("/{endpoint_method}/{api_name}/{api_version}/{endpoint_uri}",
    dependencies=[
        Depends(auth_required)
    ])
async def delete_endpoint(endpoint_method: str, api_name: str, api_version: str, endpoint_uri: str, Authorize: AuthJWT = Depends()):
    try:
        if not await platform_role_required_bool(Authorize.get_jwt_subject(), 'manage_endpoints'):
            return JSONResponse(content={"error": "You do not have permission to delete endpoints"}, status_code=403)
        return process_response(await EndpointService.delete_endpoint(endpoint_method, api_name, api_version, '/' + endpoint_uri))
    except ValueError as e:
        return JSONResponse(content={"error": "Unable to process request"}, status_code=500)
    
@endpoint_router.get("/{api_name}/{api_version}/{endpoint_uri}",
    dependencies=[
        Depends(auth_required)
    ])
async def get_endpoint(api_name: str, api_version: str, endpoint_uri: str, request: Request, Authorize: AuthJWT = Depends()):
    try:
        return process_response(await EndpointService.get_endpoint(request.method, api_name, api_version, '/' + endpoint_uri))
    except ValueError as e:
        return JSONResponse(content={"error": "Unable to process request"}, status_code=500)

"""
Get endpoints *platform endpoint.
"""
@endpoint_router.get("/{api_name}/{api_version}",
    dependencies=[
        Depends(auth_required)
    ])
async def get_endpoints_by_name_version(api_name: str, api_version: str, Authorize: AuthJWT = Depends()):
    try:
        return process_response(await EndpointService.get_endpoints_by_name_version(api_name, api_version))
    except ValueError as e:
        return JSONResponse(content={"error": "Unable to process request"}, status_code=500)