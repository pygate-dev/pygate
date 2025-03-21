"""
The contents of this file are property of pygate.org
Review the Apache License 2.0 for valid authorization of use
See https://github.com/pypeople-dev/pygate for more information
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT

from services.user_service import UserService
from utils.auth_util import auth_required
from utils.whitelist_util import whitelist_check
from utils.role_util import role_required
from models.user_model import UserModel

user_router = APIRouter()

"""
Create user *platform endpoint.
Request:
{
    "username": "<string>",
    "email": "<string>",
    "password": "<string>"
    "role": "<string>"
    "groups": ["<string>"],
    "rate_limit": "<int>",
    "rate_limit_duration": "<int>",
    "throttle": "<int>",
    "throttle_duration": "<int>"
}
Response:
{
    "message": "User created successfully",
    "user_details" {
        "user_id": "<string>",
        "email": "<string>"
    }
}
"""
@user_router.post("")
async def create_user(user_data: UserModel, Authorize: AuthJWT = Depends()):
    try:
        auth_required()
        role_required(["admin", "dev", "platform"])
        new_user = await UserService.create_user(user_data)
        return JSONResponse(content={"message": "User created successfully"}, status_code=201)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

"""
Update user *platform endpoint.
Request:
{
    "email": "<string>",
    "role": "<string>",
    "groups": ["<string>"]
}
Response:
{
    "message": "User updated successfully",
    "user_details" {
        "user_id": "<string>",
        "email": "<string>"
    }
}
"""
@user_router.put("/{user_id}")
@auth_required()
@whitelist_check()
@role_required(["admin", "dev", "platform"])
async def update_user(user_id: str, request: Request):
    try:
        update_data = await request.json()
        updated_user = await UserService.update_user(user_id, update_data)
        return JSONResponse(content={"message": "User updated successfully", "user": updated_user}, status_code=200)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

"""
Update user *platform endpoint.
Request:
{
    "current_password": "<string>",
    "new_password": "<string>"
}
Response:
{
    "message": "Password updated successfully"
}
"""
@user_router.put("/{user_id}/update-password")
@auth_required()
@whitelist_check()
@role_required(["admin", "dev", "platform"])
async def update_user_password(user_id: str, request: Request):
    try:
        data = await request.json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        if not current_password:
            raise HTTPException(status_code=400, detail="Current password is required")
        if not new_password:
            raise HTTPException(status_code=400, detail="New password is required")
        await UserService.update_password(user_id, current_password, new_password)
        return JSONResponse(content={"message": "Password updated successfully"}, status_code=200)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

"""
Get user by username *platform endpoint.
Request:
{
}
Response:
{
    "username": "<string>",
    "email": "<string>",
    "password": "<string>"
    "role": "<string>"
    "groups": ["<string>"]
}
"""
@user_router.get("/{username}")
@auth_required()
@whitelist_check()
@role_required(["admin", "dev", "platform"])
async def get_user_by_username(username: str):
    try:
        user = await UserService.get_user_by_username(username)
        return JSONResponse(content=user, status_code=200)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

"""
Get user by email *platform endpoint.
Request:
{
}
Response:
{
    "username": "<string>",
    "email": "<string>",
    "password": "<string>"
    "role": "<string>"
    "groups": ["<string>"]
}
"""
@user_router.get("/email/{email}")
@auth_required()
@whitelist_check()
@role_required(["admin", "dev", "platform"])
async def get_user_by_email(email: str):
    try:
        user = await UserService.get_user_by_email(email)
        return JSONResponse(content=user, status_code=200)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))