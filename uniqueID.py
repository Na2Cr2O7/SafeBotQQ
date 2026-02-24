import hashlib

def uid(s):
    # 使用 SHA-256 算法生成哈希
    hash_object = hashlib.sha256(s.encode())
    # 获取十六进制哈希值
    hex_dig = hash_object.hexdigest()
    # 将十六进制字符串转换为整数
    # 这里取后16位以控制整数大小，可根据需要调整
    return int(hex_dig, 16)
def suid(s):
    return f'{uid(s)}'