"""
The contents of this file are property of pygate.org
Review the Apache License 2.0 for valid authorization of use
See https://github.com/pypeople-dev/pygate for more information
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
import logging

from services.user_service import UserService
from utils.token import create_access_token
from utils.auth_util import auth_required
from utils.auth_blacklist import TimedHeap, jwt_blacklist

authorization_router = APIRouter()

"""
Login endpoint
Request:
{
    "email": "<string>",
    "password": "<string>"
}
Response:
{
    "access_token": "<string>",
    "token_type": "bearer"
}
"""
@authorization_router.post("/authorization")
async def login(request: Request, Authorize: AuthJWT = Depends()):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Missing email or password"
        )
    try:
        user = await UserService.check_password_return_user(email, password)
        access_token = create_access_token({"sub": user["username"], "role": user["role"]}, Authorize)
        response = JSONResponse(content={"access_token": access_token}, media_type="application/json")
        Authorize.set_access_cookies(access_token, response)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )

"""
Status endpoint
Request:
{
}
Response:
{
}
"""
@authorization_router.get("/authorization/status")
async def status(Authorize: AuthJWT = Depends()):
    try:
        auth_required()
        return JSONResponse(content={"status": "authorized"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
        
"""
Logout endpoint
Request:
{
}
Response:
{
    "message": "Your token has been invalidated"
}
"""
@authorization_router.post("/authorization/invalidate")
async def logout(response: Response, Authorize: AuthJWT = Depends()):
    try:
        auth_required()
        jwt_id = Authorize.get_raw_jwt()['jti']
        user = Authorize.get_jwt_subject()
        Authorize.unset_jwt_cookies(response)
        if user not in jwt_blacklist:
            jwt_blacklist[user] = TimedHeap()
        jwt_blacklist[user].push(jwt_id)
        return JSONResponse(content={"message": "Your token has been invalidated"}, status_code=200)
    except AuthJWTException as e:
        logging.error(f"Logout failed: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": "An error occurred during logout"})
    except ValueError as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    
@authorization_router.api_route("/status", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def rest_gateway():
    return JSONResponse(content={"message": "Gateway is online"}, status_code=200)