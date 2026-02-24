import requests
import json
import time
with open('debugText.txt','r',encoding='utf8') as f:
    debug_str=f.read()
# ==================== 配置 ====================
BASE_URL = "http://127.0.0.1:5700"
ACCESS_TOKEN = "aaaa"  # 如果 config.ini 中配置了 token，请填写

HEADERS = {
    "Content-Type": "application/json"
}

if ACCESS_TOKEN:
    HEADERS["Authorization"] = f"Bearer {ACCESS_TOKEN}"

# ==================== 测试工具函数 ====================
def test_action(action: str, params: dict = None, expect_success: bool = True):
    """测试单个动作"""
    url = f"{BASE_URL}"
    payload = {
        "action": action,
        "params": params or {}
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=300)
        result = response.json()
        
        status = "✅" if (result.get("status") == "ok") == expect_success else "❌"
        retcode = result.get("retcode", -1)
        
        print(f"{status} {action}")
        print(f"   返回: status={result.get('status')}, retcode={retcode}")
        
        if result.get("data"):
            data_str = json.dumps(result.get("data"), ensure_ascii=False, indent=2)
            # 只显示前 200 字符
            if len(data_str) > 200:
                print(f"   数据: {data_str[:200]}...")
            else:
                print(f"   数据: {data_str}")
        
        return result.get("status") == "ok"
        
    except Exception as e:
        print(f"❌ {action} - 异常: {e}")
        return False

# ==================== 测试用例 ====================
def test_all():
    """运行所有测试"""
    print("=" * 60)
    print("🤖 OneBot API 测试脚本")
    print("=" * 60)
    print(f"📡 服务器地址: {BASE_URL}")
    print(f"🔑 Access Token: {'已启用' if ACCESS_TOKEN else '未启用'}")
    print("=" * 60)
    
    results = {}
    
    # --- 基础信息 ---
    print("\n📌 【基础信息】")
    results["get_version"] = test_action("get_version")
    results["get_self_info"] = test_action("get_self_info")
    results["get_status"] = test_action("get_status")
    results["get_version_info"] = test_action("get_version_info")
    
    # --- 消息相关 ---
    print("\n📌 【消息相关】")
    results["send_message_private"] = test_action(
        "send_message",
        {"detail_type": "private", "user_id": "2", "message": debug_str}
    )
    results["send_message_group"] = test_action(
        "send_message",
        {"detail_type": "group", "group_id": "1", "message": debug_str}
    )
    # OneBot 11 兼容
    results["send_private_msg"] = test_action(
        "send_private_msg",
        {"user_id": 123456, "message": debug_str}
    )
    results["send_group_msg"] = test_action(
        "send_group_msg",
        {"group_id": 123456, "message": debug_str}
    )
    results["get_msg"] = test_action("get_msg", {"message_id": 3})
    
    # --- 好友相关 ---
    print("\n📌 【好友相关】")
    results["get_friend_list"] = test_action("get_friend_list")
    results["get_user_info"] = test_action("get_user_info", {"user_id": "1"})
    results["send_like"] = test_action("send_like", {"user_id": 2, "times": 6})
    
    # --- 群组相关 ---
    print("\n📌 【群组相关】")
    results["get_group_info"] = test_action("get_group_info", {"group_id": "1"})
    results["get_group_list"] = test_action("get_group_list")
    results["get_group_member_list"] = test_action("get_group_member_list", {"group_id": "1"})
    
    
    # --- 错误测试 ---
    print("\n📌 【错误测试】")
    results["unknown_action"] = test_action("unknown_action", expect_success=False)
    results["send_message_no_params"] = test_action("send_message", {}, expect_success=False)
    
    # ==================== 测试结果统计 ====================
    print("\n" + "=" * 60)
    print("📊 测试结果统计")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📈 通过率: {passed/total*100:.1f}%")
    
    if failed > 0:
        print("\n❌ 失败的测试:")
        for name, result in results.items():
            if not result:
                print(f"   - {name}")
    
    print("=" * 60)
    
    return failed == 0

# ==================== 运行测试 ====================
if __name__ == "__main__":
    try:
        # 先检查服务器是否可达
        print("🔍 检查服务器连接...")
        requests.get(BASE_URL, timeout=2)
    except:
        print(f"❌ 无法连接到服务器 {BASE_URL}")
        print("💡 请先启动 OneBot API 服务器")
        exit(1)
    
    success = test_all()
    exit(0 if success else 1)