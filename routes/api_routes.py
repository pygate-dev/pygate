"""
The contents of this file are property of pygate.org
Review the Apache License 2.0 for valid authorization of use
See https://github.com/pypeople-dev/pygate for more information
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT

from services.api_service import ApiService
from utils.auth_util import auth_required
from models.api_model import ApiModel
from utils.role_util import platform_role_required_bool

api_router = APIRouter() 

"""
Create API *platform endpoint.
Request:
{
    "api_name": "<string>",
    "api_version": "<string>",
    "api_description": "<string>",
    "api_servers": ["<string>"],
    "api_type": "<string>"
}
Response:
{
    "message": "API created successfully"
}
"""
@api_router.post("",
    dependencies=[
        Depends(auth_required)
    ])
async def create_api(api_data: ApiModel, Authorize: AuthJWT = Depends()):
    try:
        if not await platform_role_required_bool(Authorize.get_jwt_subject(), 'manage_apis'):
            return JSONResponse(content={"error": "You do not have permission to create APIs"}, status_code=403)
        await ApiService.create_api(api_data)
        return JSONResponse(content={'message': 'API created successfully'}, status_code=201)
    except ValueError as e:
        return JSONResponse(content={"error": "Unable to process request"}, status_code=400)

"""
Get API *platform endpoint.
Request:
{
}
Response:
{
    "api_name": "<string>",
    "api_version": "<string>",
    "api_description": "<string>",
    "api_path": "<string>"
}
"""
@api_router.get("/{api_name}/{api_version}",
    dependencies=[
        Depends(auth_required)
    ])
async def get_api_by_name_version(api_name: str, api_version: str):
    try:
        api = await ApiService.get_api_by_name_version(api_name, api_version)
        if api.get('_id'): del api['_id']
        return JSONResponse(content=api, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"error": "Unable to process request"}, status_code=400)

"""
Get All Accessable APIs *platform endpoint.
Request:
{
}
Response:
{
    "api_name": "<string>",
    "api_version": "<string>",
    "api_description": "<string>",
    "api_path": "<string>"
}
"""
@api_router.get("/all",
    dependencies=[
        Depends(auth_required)
    ])
async def get_all_apis(page: int = 1, page_size: int = 10):
    try:
        apis = await ApiService.get_apis(page, page_size)
        return JSONResponse(content=apis, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"error": "Unable to process request"}, status_code=400)