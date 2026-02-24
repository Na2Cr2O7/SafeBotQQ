
from guioperation.guiOperations import send_like_, send_message_
from onebotserver import *  
import uuid
import logging
import time
import enum
from log import logger
import configparser
import sqlcontroller


try:
    i = configparser.ConfigParser()
    i.read("config.ini", encoding="utf-8")
except Exception as e:
    raise RuntimeError(f"Failed to load config.ini: {e}")

def send_message(detail_type: str, detail_id: str, message: str):
    """发送消息"""
    try:
        # 直接用字符串比较，不要用 Enum
        if detail_type not in ["private", "group"]:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": {},
                "message": "Unsupported detail_type"
            }
        
        if not detail_id:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": {},
                "message": "Missing user_id or group_id"
            }
        
        if not message:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": {},
                "message": "Missing message"
            }
        try:
            message_id=send_message_(detail_type, detail_id, message,timeout=60)
        except FileNotFoundError as e:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": {},
                "message": str(e)
            }
        except TimeoutError as e:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": {},
                "message": str(e)
            }
        
        return {
            "status": "ok",
            "retcode": 0,
            "data": {
                "message_id": message_id,
                "time": time.time()
            },
            "message": ""
        }
        
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        return {
            "status": "failed",
            "retcode": 500,
            "data": {},
            "message": "Internal Error"
        }

def basic_return(retcode: int, status: str, data: dict = None, message: str = ""): # type: ignore
    """构建标准返回结构"""
    return {
        "status": status,
        "retcode": retcode,
        "data": data or {},
        "message": message
    }

def get_friend_list():
    """
    获取好友列表
    返回 OneBot 12 标准格式
    """
    userdb=sqlcontroller.UserDatabase()

    try:
        friend_list = [
        ]
        data=userdb.get_all_users()
        if data:
            friend_list=[x.to_dict() for x in data]
        
        return {
            "status": "ok",
            "retcode": 0,
            "data": friend_list,
            "message": ""
        }
        
    except Exception as e:
        logger.error(f"Error in get_friend_list: {e}")
        return {
            "status": "failed",
            "retcode": 500,
            "data": [],
            "message": "Internal Error"
        }
def get_user_info(user_id: str):
    """获取用户信息"""

    try:
        if not user_id:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": {},
                "message": "Missing user_id"
            }
        
        userdb=sqlcontroller.UserDatabase()
        user=userdb.get_user(user_id)
        if user is None:
            raise Exception("用户不存在")
        return {
            "status": "ok",
            "retcode": 0,   
            "data": {
                "user_id": user.user_id,
                "user_name": user.user_name,
                "user_displayname": user.user_displayname,
                "user_remark": user.user_remark
            },
            "message": ""
        }
    except Exception as e:
        logger.error(f"Error in get_user_info: {e}")
        return {
            "status": str(e),
            "retcode": 500,
            "data": {},
            "message": "Internal Error"
        }
# def get_group_info(group_id: str):
#     """获取群信息"""
#     try:
#         if not group_id:
#             return {
#                 "status": "failed",
#                 "retcode": 10004,
#                 "data": {},
#                 "message": "Missing group_id"
#             }
        
#         db = sqlcontroller.GroupDatabase()
#         group = db.get_group(group_id)
#         if not group:
#             return {
#                 "status": "failed",
#                 "retcode": 10005,
#                 "data": {},
#                 "message": "Group not found"
#             }
        
#         return {
#             "status": "ok",
#             "retcode": 0,
#             "data": group.to_dict(),
#             "message": ""
#         }
#     except Exception as e:
#         logger.error(f"Error in get_group_info: {e}")
#         return {
#             "status": "failed",
#             "retcode": 500,
#             "data": {},
#             "message": "Internal Error"
#         }
    
def get_group_list():
    """获取群列表"""
    try:
        db=sqlcontroller.GroupDatabase()
        r=db.get_all_groups()
        group_list = [ group.to_dict() for group in r
        ]
        
        return {
            "status": "ok",
            "retcode": 0,
            "data": group_list,
            "message": ""
        }
    except Exception as e:
        logger.error(f"Error in get_group_list: {e}")
        return {
            "status": "failed",
            "retcode": 500,
            "data": [],
            "message": "Internal Error"
        }
    
def upload_file(params: dict):
    """上传文件"""
    try:
        file_type = params.get("type")
        file_name = params.get("name")
        
        if not file_type or not file_name:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": {},
                "message": "Missing type or name"
            }
        
        # 根据 type 处理不同上传方式
        if file_type == "url":
            url = params.get("url")
            headers = params.get("headers", {})
            if not url:
                return {
                    "status": "failed",
                    "retcode": 10004,
                    "data": {},
                    "message": "Missing url for type=url"
                }
            # TODO: 从 URL 下载文件
            logger.info(f"Downloading file from URL: {url}")
            
        elif file_type == "path":
            path = params.get("path")
            if not path:
                return {
                    "status": "failed",
                    "retcode": 10004,
                    "data": {},
                    "message": "Missing path for type=path"
                }
            # TODO: 从路径读取文件
            logger.info(f"Reading file from path: {path}")
            
        elif file_type == "data":
            data = params.get("data")
            sha256 = params.get("sha256")
            if not data:
                return {
                    "status": "failed",
                    "retcode": 10004,
                    "data": {},
                    "message": "Missing data for type=data"
                }
            # TODO: 处理二进制数据
            logger.info(f"Processing file data, sha256: {sha256}")
            
        else:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": {},
                "message": f"Unsupported file type: {file_type}"
            }
        
        # 生成 file_id
        file_id = str(uuid.uuid4())
        
        # TODO: 实际存储文件逻辑
        
        return {
            "status": "ok",
            "retcode": 0,
            "data": {
                "file_id": file_id
            },
            "message": ""
        }
        
    except Exception as e:
        logger.error(f"Error in upload_file: {e}")
        return {
            "status": "failed",
            "retcode": 500,
            "data": {},
            "message": "Internal Error"
        }
def get_msg(message_id: int):
    """获取消息详情"""
    message_id_string=str(message_id)
    try:
        if not message_id:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": {},
                "message": "Missing message_id"
            }
        
        db=sqlcontroller.PrivateMessageDB()
        userDB=sqlcontroller.UserDatabase()
        message=db.get_by_message_id(message_id_string)
        if not message:
            return {
                "status": "failed",
                "retcode": 10005,
                "data": {},
                "message": "Message not found"
            }
        nickname=userDB.get_user(message.user_id)
        if nickname==None:
            nickname=""
        return {
            "status": "ok",
            "retcode": 0,
            "data": {
                "time": message.create_time,
                "message_type": message.message_type,  
                "message_id": message_id,
                "real_id": message_id,
                "sender": {
                    "user_id": message.user_id,
                    "nickname": nickname,
                    "sex": "unknown",
                    "age": 0
                },
                "message": [
                    {
                        "type": "text",
                        "data": {
                            "text": message.message
                        }
                    }
                ]
            },
            "message": ""
        }
        
    except Exception as e:
        logger.error(f"Error in get_msg: {e}")
        return {
            "status": "failed",
            "retcode": 500,
            "data": {},
            "message": "Internal Error"
        }
    
def send_like(user_id: int, times: int = 1):
    """发送好友赞"""
    try:
        if not user_id:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": {},
                "message": "Missing user_id"
            }
        
        # 限制次数 1-10
        times = max(1, min(10, int(times)))
        
        try:
            if len(str(user_id)) > 16:
                raise FileNotFoundError("this user_id cannot be found COZ it's generated by md5")
            send_like_(str(user_id), times)
        except FileNotFoundError as e:
            return {
                "status": "user_id not found",
                "retcode": 10005,
                "data": {},
                "message": str(e)
            }
        except TimeoutError as e:
            return {
                "status": "Timeout",
                "retcode": 10006,
                "data": {},
                "message": str(e)
            }
        # TODO: 调用实际点赞接口
        logger.info(f"Sending like to user {user_id}, times: {times}")
        
        return {
            "status": "ok",
            "retcode": 0,
            "data": {},
            "message": ""
        }
        
    except Exception as e:
        logger.error(f"Error in send_like: {e}")
        return {
            "status": "failed",
            "retcode": 500,
            "data": {},
            "message": "Internal Error"
        }
def get_group_info(group_id):
    group_id = str(group_id)

    try:
        if not group_id:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": [],
                "message": "Missing group_id"
            }
        db=sqlcontroller.GroupDatabase()
        group=db.get_group(group_id)
        if not group:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": [],
                "message": "not_found"
            }        
        return {
            "status": "ok",
            "retcode": 0,
            "data": {
                "group_id": group.group_id,
                "group_name": group.group_name,
            },
            "message": ""
        }
        
    except Exception as e:
        logger.error(f"Error in get_group_member_list: {e}")
        return {
            "status": "failed",
            "retcode": 500,
            "data": [],
            "message": "Internal Error"
        }
def get_group_member_list(group_id: str):
    """获取群成员列表"""
    group_id = str(group_id)

    try:
        if not group_id:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": [],
                "message": "Missing group_id"
            }
        db=sqlcontroller.GroupMemberDatabase()
        members = db.get_by_group(group_id)
        member_list=[
            {
                "group_id": group_id,
                "user_id": member.user_id,
                "nickname":member.nickname,
                "card": member.card,
                "sex": "",
                "age": 0,
                "area": "",
                "join_time": int(time.time()),
                "last_sent_time": int(time.time()),
                "level": "0",
                "role": "0",
                "unfriendly": False,
                "title": "0",
                "title_expire_time": 0,
                "card_changeable": False
            } for member in members
        ]

        
        return {
            "status": "ok",
            "retcode": 0,
            "data": member_list,
            "message": ""
        }
        
    except Exception as e:
        logger.error(f"Error in get_group_member_list: {e}")
        return {
            "status": "failed",
            "retcode": 500,
            "data": [],
            "message": "Internal Error"
        }
def get_image(file: str):
    """获取图片文件路径"""
    try:
        if not file:
            return {
                "status": "failed",
                "retcode": 10004,
                "data": {},
                "message": "Missing file"
            }
        
        # TODO: 根据实际存储路径生成文件路径
        # 示例：将文件名映射到本地存储路径
        image_path = f"/data/image/{file}"
        
        # 可选：检查文件是否存在
        # import os
        # if not os.path.exists(image_path):
        #     return {
        #         "status": "failed",
        #         "retcode": 10004,
        #         "data": {},
        #         "message": "Image not found"
        #     }
        
        logger.info(f"Getting image: {file} -> {image_path}")
        
        return {
            "status": "ok",
            "retcode": 0,
            "data": {
                "file": image_path
            },
            "message": ""
        }
        
    except Exception as e:
        logger.error(f"Error in get_image: {e}")
        return {
            "status": "failed",
            "retcode": 500,
            "data": {},
            "message": "Internal Error"
        }
    
def get_status():
    """获取运行状态"""
    try:
        return {
            "status": "ok",
            "retcode": 0,
            "data": {
                "online": True,   # QQ 在线
                "good": True,     # 状态正常
            },
            "message": ""
        }
    except Exception as e:
        logger.error(f"Error in get_status: {e}")
        return {
            "status": "failed",
            "retcode": 500,
            "data": {
                "online": None,
                "good": False
            },
            "message": "Internal Error"
        }


def get_version_info():
    """获取版本信息"""
    try:
        return {
            "status": "ok",
            "retcode": 0,
            "data": {
                "app_name": "OneBot-12-QQ",
                "app_version": i.get('general', 'version', fallback='1.0.0'),
                "protocol_version": "v11",
                "onebot_version": "12",
                "impl": "OneBot-12-QQ"
            },
            "message": ""
        }
    except Exception as e:
        logger.error(f"Error in get_version_info: {e}")
        return {
            "status": "failed",
            "retcode": 500,
            "data": {},
            "message": "Internal Error"
        }