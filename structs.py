import json
class User:
    def __init__(self, user_id: str="", user_name: str="", 
                 user_displayname: str="", user_remark: str=""):
        self.user_id = user_id
        self.user_name = user_name
        self.user_displayname = user_displayname
        self.user_remark = user_remark
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_displayname": self.user_displayname,
            "user_remark": self.user_remark
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            user_id=data.get("user_id", ""),
            user_name=data.get("user_name", ""),
            user_displayname=data.get("user_displayname", ""),
            user_remark=data.get("user_remark", "")
        )
    
    def __str__(self):
        return str(self.to_dict())
    
    def __repr__(self):
        return repr(self.to_dict())
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, User):
            return False
        return self.user_id == value.user_id
    
from dataclasses import dataclass

'''                "group_id": group_id,
                "group_name": "一群大笨蛋"
                '''
@dataclass
class Group:
    group_id: str
    group_name: str
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Group):
            return False
        return self.group_id == value.group_id
    
    def __contains__(self, item: list) -> bool:
        for group in item:
            if self == group:
                return True
        return False
    
    def to_dict(self):
        return {
            "group_id": self.group_id,
            "group_name": self.group_name
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            group_id=data.get("group_id", ""),
            group_name=data.get("group_name", "")
        )
import sqlite3
from typing import List, Optional
from dataclasses import dataclass, asdict
from contextlib import contextmanager

@dataclass
class GroupMember:
    group_id: str
    user_id: str
    nickname: str = ""
    card: str = ""
    id=0
    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

# from datetime import datetime
import time
@dataclass
class PrivateMessage:
    message_type: str
    message_id: str
    user_id: str
    message: str
    raw_message: str
    create_time: str = ""  # 自动添加时间戳字段

    def __init__(self, **kwargs) -> None:
        # 设置默认值
        self.create_time = kwargs.get('create_time', time.time())
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        
        return {
            'message_type': self.message_type,
            'message_id': self.message_id,
            'user_id': self.user_id,
            'message': self.message,
            'raw_message': self.raw_message,
            'create_time': self.create_time
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PrivateMessage':
        """从字典创建实例"""
        return cls(**data)

