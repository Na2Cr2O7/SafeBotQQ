
import focus as fc
import configparser
from  guioperation.InputEvent import *
import guioperation.positions as positions
i=configparser.ConfigParser()
from time import sleep 
i.read("config.ini",encoding='utf-8')
# i['general']['width']='1280'
i.set('general','width','1280')
i.set('general','height','720')

i.set('general','scale','1')
i.write(open('config.ini', 'w',encoding='utf-8'))
import guioperation.imageWin as imageWin
import guioperation.recognize as recognize
import cv2
def is_buttom(x,y,w,h):
    imageWin.screenshot(x,y,w,h)
    f1=cv2.imread('screenshot.bmp')
    scroll_down()
    imageWin.screenshot(x,y,w,h)
    f2=cv2.imread('screenshot.bmp')
    return recognize.similarity(f1,f2)==0.8

    


    
def focus():
    fc.focus_func(True)
def extract_all_text_from_screenshot():
    return recognize.extract_all_text_from_file("screenshot.bmp",debug=False)
def check_contacts():
    click(*positions.CONTACT_BUTTON)
    unused_texts=["我的手机"]
    contacts=[]
    sleep(0.1)
    imageWin.screenshot(*positions.LEFT_PANEL_BBOX);
    click(positions.LEFT_PANEL_BBOX[2],positions.LEFT_PANEL_BBOX[3])
    scroll_down()
    for texts in extract_all_text_from_screenshot():
        unused_texts.append(str(texts))
        if texts.text=="好友":
            click(*texts.get_center())
    print(unused_texts)
    while not is_buttom(*positions.LEFT_PANEL_BBOX):
        btn=recognize.match_expand_buttons()
        if(len(btn)<1):
            break;
        click(*btn[0])
        imageWin.screenshot2(*positions.LEFT_PANEL_BBOX)
        for texts in extract_all_text_from_screenshot():
            if str(texts) in unused_texts:
                continue
            click(*texts.get_center())
            # sleep(0.1)
            imageWin.screenshot2(*positions.INFO_BBOX)



    

if __name__ == '__main__':
    # focus()
    imageWin.screenshot(0,0,1280,720)
    print(extract_all_text_from_screenshot())