"""
The contents of this file are property of pygate.org
Review the Apache License 2.0 for valid authorization of use
See https://github.com/pypeople-dev/pygate for more information
"""

from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from utils.auth_blacklist import jwt_blacklist

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger("pygate.gateway")

async def auth_required(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        jwt_subject = Authorize.get_jwt_subject()
        jwt_id = Authorize.get_raw_jwt()['jti']
        if jwt_subject in jwt_blacklist and jwt_id in jwt_blacklist[jwt_subject]:
            raise HTTPException(
                status_code=401,
                detail="Token has been revoked"
            )
    except Exception as e:
        logger.error("Unauthorized access")
        raise HTTPException(status_code=401, detail="Unauthorized")
    return Authorize