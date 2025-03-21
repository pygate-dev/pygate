"""
The contents of this file are property of pygate.org
Review the Apache License 2.0 for valid authorization of use
See https://github.com/pypeople-dev/pygate for more information
"""

from utils.database import db
from utils.cache import cache_manager
from services.cache import pygate_cache
from models.group_model import GroupModel

class GroupService:
    group_collection = db.group

    @staticmethod
    async def create_group(data: GroupModel):
        """
        Onboard a group to the platform.
        """
        if pygate_cache.get_cache('group_cache', data.group_name) or GroupService.group_collection.find_one({'group_name': data.group_name}):
            raise ValueError("Group already exists")
        group_dict = data.dict()
        insert_result = GroupService.group_collection.insert_one(group_dict)
        if not insert_result.acknowledged:
            raise ValueError("Database error: Unable to insert group")
        group_dict['_id'] = str(insert_result.inserted_id)
        pygate_cache.set_cache('group_cache', data.group_name, group_dict)

    @staticmethod
    @cache_manager.cached(ttl=300)
    async def group_exists(data):
        """
        Check if a group exists.
        """
        if pygate_cache.get_cache('group_cache', data.get('group_name')) or GroupService.group_collection.find_one({'group_name': data.get('group_name')}):
            return True
        return False

    @staticmethod
    @cache_manager.cached(ttl=300)
    async def get_groups(page=1, page_size=10):
        """
        Get all groups.
        """
        skip = (page - 1) * page_size
        cursor = GroupService.group_collection.find().sort('api_name', 1).skip(skip).limit(page_size)
        groups = cursor.to_list(length=None)
        for group in groups:
            if group.get('_id'): del group['_id']
        if not groups:
            raise ValueError("No APIs found")
        return groups

    @staticmethod
    @cache_manager.cached(ttl=300)
    async def get_group(group_name):
        """
        Get a group by name.
        """
        group = pygate_cache.get_cache('group_cache', group_name) or GroupService.group_collection.find_one({'group_name': group_name})
        if not group:
            raise ValueError("Group not found")
        if group.get('_id'): del group['_id']
        return group