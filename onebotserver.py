import http.server
import socketserver
import json
import logging
import threading
import time
import uuid
import requests
from urllib.parse import urlparse, parse_qs
import enum
import configparser

from co import *
from log import logger

# 配置读取优化：增加异常处理
try:
    i = configparser.ConfigParser()
    i.read("config.ini", encoding="utf-8")
except Exception as e:
    raise RuntimeError(f"Failed to load config.ini: {e}")

# 常量定义
PORT = 5700
ACCESS_TOKEN = i.get("general", "access_token", fallback="").strip()
if ACCESS_TOKEN=='null':
    ASSESS_TOKEN = False
GENERAL_REQUIRED_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": f"{i['general']['version'].replace(' ', '')}",
    "X-OneBot-Version": "12",
    "X-Impl": "OneBot-12-QQ",
}
GENERAL_REQUIRED_HEADERS_11 = {
    "Content-Type": "application/json",
    "User-Agent": f"{i['general']['version'].replace(' ', '')}",
    "X-OneBot-Version": "11",
    "X-Impl": "OneBot-11-QQ",
}
GENERAL_RETURN_HEADERS = {
    "status": "ok",
    "retcode": 0,
    "data": {},
    "message": ""
}

# 日志配置增强


class ReusableTCPServer(socketserver.TCPServer):
    """重用 TCP 服务器类"""
    allow_reuse_address = True

class OneBotAPIHandler(http.server.BaseHTTPRequestHandler):
    """OneBot API 处理类"""
    def send_general_headers(self):
        """发送通用响应头"""
        for k, v in GENERAL_REQUIRED_HEADERS.items():
            self.send_header(k, v)

    def do_POST(self):
        """处理 POST 请求"""
        try:
            # 内容类型校验
            content_type = self.headers.get("Content-Type")
            if content_type != "application/json":
                self.send_response(400)
                self.send_general_headers()
                self.end_headers()
                self.wfile.write(b"Invalid Content-Type")
                return

            # 访问令牌校验（修复空白字符问题）
            auth_header = self.headers.get("Authorization", "").strip()
            if ACCESS_TOKEN and not auth_header.startswith(f"Bearer {ACCESS_TOKEN}"):
                self.send_response(401)
                self.send_general_headers()
                self.end_headers()
                self.wfile.write(b"Unauthorized")
                return

            # 解析请求体
            content_length = int(self.headers.get("Content-Length", 0))
            request_body = self.rfile.read(content_length)
            try:
                request_data = json.loads(request_body)
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_general_headers()
                self.end_headers()
                self.wfile.write(b"Invalid JSON")
                return
            
            # 匹配动作
            action = request_data.get("action")
            logger.info(f"Received action: {action}, params: {request_data.get('params', {})}")
            
            return_data = GENERAL_RETURN_HEADERS.copy()
            
            match action:
                case "get_version":
                    return_data['data'] = {
                        "impl": "OneBot-12-QQ",
                        "version": "1.0.0",
                        "onebot_version": "12"
                    }
                case "send_message":
                    params = request_data.get("params", {})
                    detail_type = params.get("detail_type")
                    message = params.get("message")
                    
                    # 根据 detail_type 正确获取 detail_id
                    if detail_type == "group":
                        detail_id = params.get("group_id")
                    elif detail_type == "private":
                        detail_id = params.get("user_id")
                    else:
                        detail_id = None
                    
                    # send_message 直接返回完整响应结构
                    return_data = send_message(detail_type, detail_id, message) # pyright: ignore[reportArgumentType]
                case "send_private_msg":
                    params = request_data.get("params", {})
                    user_id = str(params.get("user_id"))  # OneBot 11 是 int，转为 string
                    message = params.get("message")
                    return_data = send_message("private", user_id, message)

                case "send_group_msg":
                    params = request_data.get("params", {})
                    group_id = str(params.get("group_id"))  # OneBot 11 是 int，转为 string
                    message = params.get("message")
                    return_data = send_message("group", group_id, message)
                case "get_self_info":
                    return_data['data'] = {
                        "user_id": uuid.uuid4().int >> 64,
                        "user_name": i.get('general', 'version', fallback='1.0.0'),
                        "user_displayname": ""
                    }
                case "get_friend_list":
                    return_data = get_friend_list()
                case "get_user_info":
                    params = request_data.get("params", {})
                    user_id = params.get("user_id")
                    return_data = get_user_info(user_id)
                case "get_group_info":
                    params = request_data.get("params", {})
                    group_id = params.get("group_id")
                    return_data = get_group_info(group_id)
                case "get_group_list":
                    return_data = get_group_list()
                case "upload_file":
                    params = request_data.get("params", {})
                    return_data = upload_file(params)

                case "get_msg": 
                    params = request_data.get("params", {})
                    message_id = params.get("message_id")
                    return_data = get_msg(message_id)
                case "send_like":
                    params = request_data.get("params", {})
                    user_id = params.get("user_id")
                    times = params.get("times", 1)
                    return_data = send_like(user_id, times)
                case "get_group_member_list":
                    params = request_data.get("params", {})
                    group_id = params.get("group_id")
                    return_data = get_group_member_list(group_id)
                case "get_image":
                    params = request_data.get("params", {})
                    file = params.get("file")
                    return_data = get_image(file)
                case "get_status":
                    return_data = get_status()

                case "get_version_info":
                    return_data = get_version_info()
                case _:
                    return_data.update({
                        "status": "failed", 
                        "retcode": 10004, 
                        "message": "未知动作"
                    })
            # ✅ 先发送响应头，再发送响应体
            self.send_response(200)
            self.send_general_headers()
            self.end_headers()
            self.wfile.write(json.dumps(return_data).encode("utf-8"))

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.send_response(500)
            self.send_general_headers()
            self.end_headers()
            self.wfile.write(b"Internal Server Error")
