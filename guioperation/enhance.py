import cv2
import numpy as np
def binarize(img,th):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # img = cv2.threshold(img, th, 255, cv2.THRESH_BINARY)[1]
    img[img > th] = 255
    img[img <= th] = 0
    return img

def replace_color_with_white(image, target_rgb, tolerance=30):
    """
    将图片中指定RGB颜色的部分替换成白色
    
    参数:
        image: 输入图片 (numpy array, BGR格式)
        target_rgb: 目标颜色，格式为 (R, G, B)，每个值范围 0-255
        tolerance: 颜色匹配容差，默认10，值越大匹配范围越宽
    
    返回:
        处理后的图片 (numpy array, BGR格式)
    """
    # 创建图片副本，避免修改原图
    result = image.copy()
    
    # OpenCV使用BGR格式，需要将RGB转换为BGR
    target_bgr = (target_rgb[2], target_rgb[1], target_rgb[0])
    
    # 定义颜色范围的下限和上限
    lower_bound = np.array([
        max(0, target_bgr[0] - tolerance),
        max(0, target_bgr[1] - tolerance),
        max(0, target_bgr[2] - tolerance)
    ], dtype=np.uint8)
    
    upper_bound = np.array([
        min(255, target_bgr[0] + tolerance),
        min(255, target_bgr[1] + tolerance),
        min(255, target_bgr[2] + tolerance)
    ], dtype=np.uint8)
    
    # 创建颜色掩码
    mask = cv2.inRange(image, lower_bound, upper_bound)
    
    # 将掩码区域替换为白色 (BGR: 255, 255, 255)
    result[mask > 0] = [255, 255, 255]
    
    return result