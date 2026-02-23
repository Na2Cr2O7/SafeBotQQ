from configparser import ConfigParser
import threading
from onebotserver import *
import subprocess
import guioperation.guiOperations as guiOperations
guiOperations.focus()
input("请按回车键启动服务器")
# 启动服务器
subprocess.Popen(["scaletoini.exe"])
def start_server():
    try:
        with ReusableTCPServer(("", PORT), OneBotAPIHandler) as httpd:
                logger.info(f"🤖 OneBot API Server running on port {PORT}")
                logger.info(f"📡 Access Token: {'Enabled' if ACCESS_TOKEN else 'Disabled'}")
                httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")

# threading.Thread(target=start_server, daemon=True).start()
logger.info("启动服务器")
start_server()
