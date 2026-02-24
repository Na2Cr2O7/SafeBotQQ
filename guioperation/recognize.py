import requests
import json
import configparser
import base64
from typing import List, Union
# from PIL import Image
import cv2
import numpy as np

class Texts(object):
    def __init__(self, text="", bbox=[0,0,0,0]):
        self.text = text
        self.bbox = bbox
    def __str__(self):
        return self.text
    def __repr__(self):
        return self.text + " " + str(self.bbox)
    def __len__(self):
        return len(self.text)
    def get_center(self,previousx=0,previousy=0):
        return (self.bbox[0]+self.bbox[2])/2+previousx, (self.bbox[1]+self.bbox[3])/2+previousy


def extract_all_text(img_base64: str) -> List[Texts]:
    """
    调用 UmiOCR API 识别 Base64 编码的图片并返回 Texts 对象列表
    
    Args:
        img_base64: Base64 编码的图片字符串（可带或不带 data:image/png;base64, 前缀）
    
    Returns:
        List[Texts]: 识别结果列表
    """
    # 1. 读取配置文件获取服务器地址
    config = configparser.ConfigParser()
    try:
        config.read("config.ini", encoding='utf8')
        server = config.get("umiocr", "server")
    except Exception as e:
        # 默认地址
        server = "http://127.0.0.1:1224"
        print(f"警告：无法读取配置，使用默认地址 {server}")

    # 2. 清理 Base64 字符串（去除可能的 data:image/...;base64, 前缀）
    # Umi-OCR 要求纯 Base64 数据，带前缀会导致 "Base64 decode failed" 错误
    clean_base64 = img_base64
    if "," in img_base64:
        clean_base64 = img_base64.split(",", 1)[1]
    
    # 3. 准备请求参数
    options = {
        "data.format": "dict"  # 必须为 dict 才能获取 bbox 信息
        # , "ocr.language": "简体中文"
    }

    payload = {
        "base64": clean_base64,
        "options": options
    }

    headers = {"Content-Type": "application/json"}
    
    try:
        # 4. 发送 POST 请求到 /api/ocr 接口
        response = requests.post(
            f"{server}/api/ocr", 
            data=json.dumps(payload), 
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        res_json = response.json()
        
        # 5. 检查响应状态
        # Umi-OCR 成功时 code=100，失败时返回其他错误码
        # print(res_json)
        if res_json.get('code') != 100:
            error_msg = res_json.get('error', '未知错误')
            print(f"OCR 识别失败：{error_msg} (code: {res_json.get('code')})")
            return []

        # 6. 解析返回结果
        ocr_data = res_json.get('data', [])
        
        results = []
        for block in ocr_data:
            text = block.get('text', '')
            box_points = block.get('box', [])
            
            # 将四点坐标转换为 bbox [x_min, y_min, x_max, y_max]
            if len(box_points) == 4:
                xs = [p[0] for p in box_points]
                ys = [p[1] for p in box_points]
                bbox = [min(xs), min(ys), max(xs), max(ys)]
            else:
                bbox = [0, 0, 0, 0]
            
            results.append(Texts(text=text, bbox=bbox))
            
        return results

    except requests.exceptions.Timeout:
        print("API 请求超时")
        return []
    except requests.exceptions.RequestException as e:
        print(f"API 请求失败: {e}")
        return []
    except json.JSONDecodeError:
        print("响应不是有效的 JSON")
        return []


def extract_all_text_from_file(img_path: str, debug=False) -> List[Texts]:
    """
    从文件路径读取图片并调用 OCR（辅助函数）
    
    Args:
        img_path: 图片文件路径
        debug: 是否启用调试模式（在图片上绘制边界框）
    
    Returns:
        List[Texts]: 识别结果列表
    """
    # 读取图片字节
    with open(img_path, "rb") as f:
        img_bytes = f.read()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    # 调用 OCR API
    texts = extract_all_text(img_base64)
    
    # 如果启用调试模式，则绘制边界框
    if debug:
        # 使用 OpenCV 读取原始图片
        image = cv2.imread(img_path)
        if image is None:
            print(f"警告：无法用 OpenCV 读取图片 {img_path}")
            return texts
        
        # 为每个识别结果绘制边界框
        for text_obj in texts:
            x1, y1, x2, y2 = map(int, text_obj.bbox)
            # 绘制矩形框（绿色，线宽2）
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # 可选：在框上方显示文本内容（避免遮挡）
            if text_obj.text:
                # 计算文本位置（框上方）
                text_y = max(y1 - 10, 10)  # 确保不超出图像顶部
                # 绘制文本背景（半透明效果需要额外处理，这里用简单矩形）
                cv2.putText(image, text_obj.text, (x1, text_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # 显示带标注的图片
        cv2.imshow('OCR Result', image)
        cv2.waitKey(0)  # 等待按键关闭窗口
        cv2.destroyAllWindows()
    
    return texts

from guioperation.InputEvent import click
import guioperation.imageWin as imageWin

i=configparser.ConfigParser()
i.read("config.ini",encoding='utf-8')
width=i.getint('general','width')
height=i.getint('general','height')
scale=i.getfloat('general','scale')
import numpy as np
from typing import List

def match_template(src: str, target: str, threshold=0.9, debug=False) -> List[List[int, int]]: # type: ignore
    """
    模板匹配函数
    
    Args:
        src: 源图像路径
        target: 模板图像路径
        threshold: 匹配阈值 (0-1)，越高越严格
        debug: 是否启用调试模式（在源图像上绘制匹配位置）
    
    Returns:
        List[List[int, int]]: 匹配到的位置列表 [[x, y], [x, y], ...]
    """
    # 1. 读取图像
    src_image = cv2.imread(src)
    target_image = cv2.imread(target)
    
    if src_image is None:
        raise FileNotFoundError(f"无法读取源图像: {src}")
    if target_image is None:
        raise FileNotFoundError(f"无法读取模板图像: {target}")
    
    # 2. 执行模板匹配
    res = cv2.matchTemplate(src_image, target_image, cv2.TM_CCOEFF_NORMED)
    
    # 3. 获取匹配位置
    h, w = target_image.shape[:2]  # 模板图像的高和宽
    locations = np.where(res >= threshold)
    
    # 4. 非极大值抑制 (NMS) - 去除重叠的重复检测
    points = []
    for pt in zip(*locations[::-1]):  # (x, y)
        # 检查是否与已有点过于接近（避免重复）
        is_duplicate = False
        for existing_pt in points:
            # 计算两点距离，如果小于模板尺寸的一半则视为重复
            dist = np.sqrt((pt[0] - existing_pt[0])**2 + (pt[1] - existing_pt[1])**2)
            if dist < min(w, h) / 2:
                is_duplicate = True
                break
        if not is_duplicate:
            points.append((int(pt[0]), int(pt[1])))
    
    # 5. 调试模式：绘制匹配结果
    if debug and points:
        debug_image = src_image.copy()
        for pt in points:
            x, y = pt
            # 绘制矩形框
            cv2.rectangle(debug_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # 显示匹配度
            match_score = res[y, x]
            cv2.putText(debug_image, f"{match_score:.2f}", (x, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # 显示结果
        cv2.imshow('Template Match Result', debug_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    # 6. 返回匹配位置列表
    return [list(pt) for pt in points]
def match_expand_buttons():
    return match_template('screenshot.bmp','templates/more.png')
def match_copy_buttons():
    return match_template('screenshot.bmp','templates/copy.png')
def similarity(image1, image2):
    diff = cv2.absdiff(image1, image2)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    
    # 差异越小，相似度越高
    mse = np.mean(gray_diff ** 2)
    similarity_score = 1 / (1 + mse / 255.0)  # 归一化到0-1
    return similarity_score
def get_key_value(extracted_text_result_from_function_extract_all_text_from_screenshot_or_extract_all_text_from_file:List[Texts],key):
    for index,texts in enumerate(extracted_text_result_from_function_extract_all_text_from_screenshot_or_extract_all_text_from_file):
        if (texts.text).find(key) != -1:
            return extracted_text_result_from_function_extract_all_text_from_screenshot_or_extract_all_text_from_file[index+1]
    return Texts()
def get_key_value_vertical(extracted_text_result_from_function_extract_all_text_from_screenshot_or_extract_all_text_from_file:List[Texts],key):
    length=len(extracted_text_result_from_function_extract_all_text_from_screenshot_or_extract_all_text_from_file)
    semi_length=length//2
    for index,texts in enumerate(extracted_text_result_from_function_extract_all_text_from_screenshot_or_extract_all_text_from_file):
        if (texts.text).find(key) != -1:
            if index<semi_length:
                return extracted_text_result_from_function_extract_all_text_from_screenshot_or_extract_all_text_from_file[index+semi_length]
            else:
                return extracted_text_result_from_function_extract_all_text_from_screenshot_or_extract_all_text_from_file[index-semi_length]
    return Texts()

def click_text(text):
    if text=='':
        return False
    print('click text:',text)
    imageWin.screenshot2(0,0,width,height)
    found=False
    for index, texts in enumerate    (extract_all_text_from_file('screenshot.bmp')):
        if str(texts) in text or text in str(texts):
            click(*texts.get_center())
            found=True
    return found
def contains(text: str,image: str):
    result=extract_all_text_from_file(image)
    for texts in result:
        if str(texts) in text or text in str(texts):
            return True
    return False
def contains_text_on_screen(text: str):
    imageWin.screenshot(0,0,width,height)
    return contains(text,'screenshot.bmp')


# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 示例 1: 直接使用 Base64 字符串
    # 假设你已经有 base64 编码的图片数据
    # base64_image = "iVBORw0KGgoAAAANSUhEUgAA..."  # 你的 base64 数据
    texts = extract_all_text_from_file(r"D:\Pictures\1696861340288c590bec1cdc259ef6a1a78afebad4d62739196716162e583ea7a34f25456a3fb.0.jpg")
    # texts = extract_all_text(base64_image)
    for t in texts:
        print(f"文本: {t.text}, 中心点: {t.get_center()}")
    
    # 示例 2: 从文件读取并转换
    # texts = extract_all_text_from_file("test_image.png")
    
    # 示例 3: 带 data URI 前缀的 base64（代码会自动清理）
    # data_uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
    # texts = extract_all_text(data_uri)