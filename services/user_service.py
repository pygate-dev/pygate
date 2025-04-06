"""
The contents of this file are property of pygate.org
Review the Apache License 2.0 for valid authorization of use
See https://github.com/pypeople-dev/pygate for more information
"""

from models.response_model import ResponseModel
from utils import password_util
from utils.database import db
from services.cache import pygate_cache
from models.create_user_model import CreateUserModel

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger("pygate.gateway")

class UserService:
    user_collection = db.users
    subscriptions_collection = db.subscriptions
    api_collection = db.apis

    @staticmethod
    async def get_user_by_email_with_password_helper(email):
        """
        Retrieve a user by email.
        """
        user = UserService.user_collection.find_one({'email': email})
        if '_id' in user:
            del user['_id']
        if not user:
            raise ValueError("User not found")
        return user

    @staticmethod
    async def get_user_by_username_helper(username):
        """
        Retrieve a user by username.
        """
        try:
            user = pygate_cache.get_cache('user_cache', username)
            if not user:
                user = UserService.user_collection.find_one({'username': username})
                if not user:
                    raise ValueError("User not found in database")
                if user.get('_id'): del user['_id']
                if user.get('password'): del user['password']
                pygate_cache.set_cache('user_cache', username, user)
            if '_id' in user:
                del user['_id']
            if 'password' in user:
                del user['password']
            if not user:
                raise ValueError("User not found")
            return user
        except Exception as e:
            raise ValueError("User not found error" + str(e))
        
    @staticmethod
    async def get_user_by_username(username, request_id):
        """
        Retrieve a user by username.
        """
        logger.info(f"{request_id} | Getting user: {username}")
        user = pygate_cache.get_cache('user_cache', username)
        if not user:
            user = UserService.user_collection.find_one({'username': username})
            if not user:
                logger.error(f"{request_id} | User retrieval failed with code USR002")
                return ResponseModel(
                    status_code=404,
                    error_code='USR002',
                    error_message='User not found'
                ).dict()
            if user.get('_id'): del user['_id']
            if user.get('password'): del user['password']
            pygate_cache.set_cache('user_cache', username, user)
        if '_id' in user:
            del user['_id']
        if 'password' in user:
            del user['password']
        if not user:
            logger.error(f"{request_id} | User retrieval failed with code USR002")
            return ResponseModel(
                status_code=404,
                error_code='USR002',
                error_message='User not found'
            ).dict()
        logger.info(f"{request_id} | User retrieval successful")
        return ResponseModel(
            status_code=200,
            data=user
        ).dict()

    @staticmethod
    async def get_user_by_email(email, request_id):
        """
        Retrieve a user by email.
        """
        logger.info(f"{request_id} | Getting user by email: {email}")
        user = UserService.user_collection.find_one({'email': email})
        if '_id' in user:
            del user['_id']
        if 'password' in user:
            del user['password']
        if not user:
            logger.error(f"{request_id} | User retrieval failed with code USR002")
            return ResponseModel(
                status_code=404,
                error_code='USR002',
                error_message='User not found'
            ).dict()
        logger.info(f"{request_id} | User retrieval successful")
        return ResponseModel(
            status_code=200,
            data=user
        ).dict()

    @staticmethod
    async def create_user(data: CreateUserModel, request_id):
        """
        Create a new user.
        """
        logger.info(f"{request_id} | Creating user: {data.username}")
        if UserService.user_collection.find_one({'username': data.username}):
            logger.error(f"{request_id} | User creation failed with code USR001")
            return ResponseModel(
                status_code=400,
                error_code='USR001',
                error_message='Username already exists'
            ).dict()
        if UserService.user_collection.find_one({'email': data.email}):
            logger.error(f"{request_id} | User creation failed with code USR001")
            return ResponseModel(
                status_code=400,
                error_code='USR001',
                error_message='Email already exists'
            ).dict()
        data.password = password_util.hash_password(data.password)
        data_dict = data.dict()
        UserService.user_collection.insert_one(data_dict)
        if '_id' in data_dict:
            del data_dict['_id']
        if 'password' in data_dict:
            del data_dict['password']
        pygate_cache.set_cache('user_cache', data.username, data_dict)
        logger.info(f"{request_id} | User creation successful")
        return ResponseModel(
            status_code=201,
            message='User created successfully'
        ).dict()

    @staticmethod
    async def check_password_return_user(email, password):
        """
        Verify password and return user if valid.
        """
        try:
            user = await UserService.get_user_by_email_with_password_helper(email)
            if not password_util.verify_password(password, user.get('password')):
                raise ValueError("Invalid email or password")
            return user
        except Exception as e:
            raise ValueError("Authentication failed")

    @staticmethod
    async def update_user(username, update_data, request_id):
        """
        Update user information.
        """
        logger.info(f"{request_id} | Updating user: {username}")
        user = pygate_cache.get_cache('user_cache', username)
        if not user:
            user = UserService.user_collection.find_one({'username': username})
            if not user:
                logger.error(f"{request_id} | User update failed with code USR002")
                return ResponseModel(
                    status_code=404,
                    error_code='USR002',
                    error_message='User not found'
                ).dict()
        else:
            pygate_cache.delete_cache('user_cache', username)
        non_null_update_data = {k: v for k, v in update_data.dict().items() if v is not None}
        if non_null_update_data:
            update_result = UserService.user_collection.update_one({'username': username}, {'$set': non_null_update_data})
            if not update_result.acknowledged or update_result.modified_count == 0:
                logger.error(f"{request_id} | User update failed with code USR003")
                return ResponseModel(
                    status_code=400,
                    error_code='USR004',
                    error_message='Database error: Unable to update user'
                ).dict()
        if non_null_update_data.get('role'):
            await UserService.purge_apis_after_role_change(username, request_id)
        logger.info(f"{request_id} | User update successful")
        return ResponseModel(
            status_code=200,
            message='User updated successfully'
        ).dict()
    
    @staticmethod
    async def delete_user(username, request_id):
        """
        Delete a user.
        """
        logger.info(f"{request_id} | Deleting user: {username}")
        user = pygate_cache.get_cache('user_cache', username)
        if not user:
            user = UserService.user_collection.find_one({'username': username})
            if not user:
                logger.error(f"{request_id} | User deletion failed with code USR002")
                return ResponseModel(
                    status_code=404,
                    error_code='USR002',
                    error_message='User not found'
                ).dict()
        delete_result = UserService.user_collection.delete_one({'username': username})
        if not delete_result.acknowledged or delete_result.deleted_count == 0:
            logger.error(f"{request_id} | User deletion failed with code USR003")
            return ResponseModel(
                status_code=400,
                error_code='USR003',
                error_message='Database error: Unable to delete user'
            ).dict()
        pygate_cache.delete_cache('user_cache', username)
        pygate_cache.delete_cache('user_subscription_cache', username)
        logger.info(f"{request_id} | User deletion successful")
        return ResponseModel(
            status_code=200,
            message='User deleted successfully'
        ).dict()

    @staticmethod
    async def update_password(username, update_data, request_id):
        """
        Update user information.
        """
        logger.info(f"{request_id} | Updating password for user: {username}")
        hashed_password = password_util.hash_password(update_data.new_password)
        UserService.user_collection.update_one({'username': username}, {'$set': {'password': hashed_password}})
        user = UserService.user_collection.find_one({'username': username})
        if not user:
            logger.error(f"{request_id} | User password update failed with code USR002")
            return ResponseModel(
                status_code=404,
                error_code='USR002',
                error_message='User not found'
            ).dict()
        if '_id' in user:
            del user['_id']
        if 'password' in user:
            del user['password']
        pygate_cache.set_cache('user_cache', username, user)
        logger.info(f"{request_id} | User password update successful")
        return ResponseModel(
            status_code=200,
            message='User updated successfully'
        ).dict()

    @staticmethod
    async def purge_apis_after_role_change(username, request_id):
        """
        Remove subscriptions after role change.
        """
        logger.info(f"{request_id} | Purging APIs for user: {username}")
        user_subscriptions = pygate_cache.get_cache('user_subscription_cache', username) or UserService.subscriptions_collection.find_one({'username': username})
        for subscription in user_subscriptions.get('apis'):
            api_name, api_version = subscription.split('/')
            user = pygate_cache.get_cache('user_cache', username) or UserService.user_collection.find_one({'username': username})
            api = pygate_cache.get_cache('api_cache', f"{api_name}/{api_version}") or UserService.api_collection.find_one({'api_name': api_name, 'api_version': api_version})
            if api and api.get('role') and user.get('role') not in api.get('role'):
                user_subscriptions['apis'].remove(subscription)
        UserService.subscriptions_collection.update_one(
            {'username': username},
            {'$set': {'apis': user_subscriptions.get('apis', [])}}
        )
        pygate_cache.set_cache('user_subscription_cache', username, user_subscriptions)
        logger.info(f"{request_id} | Purge successful")