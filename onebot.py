from configparser import ConfigParser
import threading
from onebotserver import *
import subprocess
import guioperation.guiOperations as guiOperations
from colorama import init,Fore
from sys import argv
quick_start=False
if len(argv) >2 and argv[2]=="QuickStart":
    quick_start=True
# guiOperations.focus()
# input("请按回车键启动服务器")
# 启动服务器
subprocess.Popen(["scaletoini.exe"])
i=configparser.ConfigParser()
i.read("config.ini",'utf8')
i.set('general','screen_scale',i['general']['scale'])
i.set('general','scale','1')
i.write(open('config.ini', 'w',encoding='utf-8'))
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
if not quick_start:
    timeout=300
    print(f'{Fore.GREEN}检查通讯录，预计需要{timeout}s')
    guiOperations.check_contacts(timeout=timeout)
    guiOperations.click(*guiOperations.positions.CHAT_BUTTON)
    print(f'{Fore.GREEN}检查群组，预计需要{timeout}s')
    guiOperations.get_users_in_groups(timeout=timeout)
    guiOperations.click(*guiOperations.positions.CHAT_BUTTON)
    print(f'{Fore.GREEN}检查消息，预计需要{timeout}s')
    guiOperations.get_all_messages(timeout=timeout)

# threading.Thread(target=start_server, daemon=True).start()
logger.info("启动服务器")
print("启动服务器")
start_server()
