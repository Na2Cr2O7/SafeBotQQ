# SafeBotQQ

OCR+模板匹配的安全QQ机器人框架，适配OneBot12 协议

* 目前只支持Windows 8.1 以上系统

## 安装

1. 安装Python3.14
2. 安装依赖
```bash
pip install -r requirements.txt
```
3. 安装umi-OCR
![配置HTTP服务](image.png)

4. 配置
打开config.ini文件，修改access_token.
5. 运行
```bash
python onebot.py
```
启动服务器大概需要15分钟。

添加参数QuickStart会跳过收集联系人等步骤。加快启动速度到接近秒开

具体的测试可看test.py


## API支持情况
send_private_msg √
send_group_msg √
send_msg × 使用send_message
send_message √
delete_msg ×
get_msg √ 
get_self_info √
get_user_info √ 只获取好友信息
get_friend_list √
get_group_info √
get_group_list √
get_group_member_info ×
get_group_member_list √
set_group_name ×
leave_group  ×
两级群组接口与文件接口 ×

### 关于get_group_list
目前不能分辨群成员的群昵称和用户名，会自动给没有在联系人列表找到的联系人分配一个约77位整数（md5的十进制表示）为user_id

