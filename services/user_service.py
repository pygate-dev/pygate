"""
The contents of this file are property of pygate.org
Review the Apache License 2.0 for valid authorization of use
See https://github.com/pypeople-dev/pygate for more information
"""

from utils import password_util
from utils.database import db
from services.cache import pygate_cache
from models.user_model import UserModel

import logging

class UserService:
    user_collection = db.users

    @staticmethod
    async def get_user_by_username(username):
        """
        Retrieve a user by username.
        """
        try:
            user = pygate_cache.get_cache('user_cache', username) or UserService.user_collection.find_one({'username': username})
            logging.debug(f"Retrieved user: {user}, type: {type(user)}")
            if not user:
                raise ValueError("User not found")
            return user
        except Exception as e:
            logging.error(f"Error in get_user_by_username: {str(e)}")
            raise

    @staticmethod
    async def get_user_by_email(email):
        """
        Retrieve a user by email.
        """
        try:
            user = UserService.user_collection.find_one({'email': email})
            logging.debug(f"Retrieved user: {user}, type: {type(user)}")
            if not user:
                raise ValueError("Email not found")
            return user
        except Exception as e:
            logging.error(f"Error in get_user_by_email: {str(e)}")
            raise

    @staticmethod
    async def create_user(data: UserModel):
        """
        Create a new user.
        """
        if UserService.user_collection.find_one({'username': data.username}):
            raise ValueError("Username already exists")
        
        if UserService.user_collection.find_one({'email': data.email}):
            raise ValueError("Email already exists")

        data.password = password_util.hash_password(data.password)

        data_dict = data.dict()
        user = UserService.user_collection.insert_one(data_dict)
        data_dict['_id'] = str(user.inserted_id)
        pygate_cache.set_cache('user_cache', data.username, data_dict)

    @staticmethod
    async def check_password_return_user(email, password):
        """
        Verify password and return user if valid.
        """
        try:
            user = await UserService.get_user_by_email(email)
            
            if not password_util.verify_password(password, user.get('password')):
                raise ValueError("Invalid email or password")
            
            return user
            
        except Exception as e:
            logging.error(f"Error in check_password_return_user: {str(e)}")
            raise ValueError("Authentication failed")

    @staticmethod
    async def update_user(username, update_data):
        """
        Update user information.
        """
        if 'password' in update_data:
            update_data['password'] = password_util.hash_password(update_data.get('password'))
        
        UserService.user_collection.update_one({'username': username}, {'$set': update_data})
        
        user = UserService.user_collection.find_one({'username': username})
        if '_id' in user:
            del user['_id']
        pygate_cache.get_cache('user_cache', username, user)