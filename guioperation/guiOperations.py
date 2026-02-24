from typing import List

import structs
import sqlcontroller
import focus as fc
import configparser
from  guioperation.InputEvent import *
import guioperation.positions as positions
from uniqueID import suid, uid
config=configparser.ConfigParser()
from time import sleep 
import guioperation.enhance as enhance
from conversationStyleExtract import extract as conversationStyleExtract
import pyperclip
config.read("config.ini",encoding='utf-8')
# i['general']['width']='1280'
config.set('general','width','1280')
config.set('general','height','720')

config.set('general','scale','1')
config.write(open('config.ini', 'w',encoding='utf-8'))
import guioperation.imageWin as imageWin
import guioperation.recognize as recognize
import cv2
def is_buttom(x,y,w,h):
    imageWin.screenshot(x,y,w,h)
    f1=cv2.imread('screenshot.bmp')
    for i in range(4): scroll_down()
    imageWin.screenshot(x,y,w,h)
    f2=cv2.imread('screenshot.bmp')
    return recognize.similarity(f1,f2)==0.8

    



    
def focus():
    fc.focus_func(True)
def extract_all_text_from_screenshot():
    return recognize.extract_all_text_from_file("screenshot.bmp",debug=False)

def check_contacts(timeout=300):
    db=sqlcontroller.UserDatabase()
    db.delete_all()
    start_time=time.time()
    click(*positions.CONTACT_BUTTON)
    unused_texts=["我的手机",'>']
    contacts:List[structs.User]=[]
    sleep(0.1)
    imageWin.screenshot(*positions.LEFT_PANEL_BBOX);
    left_panel_pos=positions.get_bbox_pos(positions.LEFT_PANEL_BBOX)
    click(positions.LEFT_PANEL_BBOX[2],positions.LEFT_PANEL_BBOX[3])
    scroll_down()
    imageWin.screenshot2(*positions.LEFT_PANEL_BBOX);
    for texts in extract_all_text_from_screenshot():
        unused_texts.append(str(texts))
        if texts.text=="好友":
            sleep(1)
            click(*texts.get_center(*left_panel_pos))
            sleep(1)
    img=cv2.imread("screenshot.bmp")
    img=enhance.replace_color_with_white(img, (169, 169, 169))
    img=enhance.replace_color_with_white(img, (122, 122, 122),)
    img=enhance.binarize(img, 150)
    cv2.imwrite("bin.png", img)
    clicked=[]
    for texts in recognize.extract_all_text_from_file("bin.png"):
        if texts.text not in unused_texts:
            unused_texts.append(str(texts))
    print(unused_texts)
    click(positions.LEFT_PANEL_BBOX[2],positions.LEFT_PANEL_BBOX[3])
    while not is_buttom(*positions.LEFT_PANEL_BBOX):

        if time.time()-start_time>timeout:
            break;
        btn=recognize.match_expand_buttons()
        for b in btn:
            click(left_panel_pos[0]+b[0],left_panel_pos[1]+b[1])
        imageWin.screenshot2(*positions.LEFT_PANEL_BBOX)
        # imageWin.screenshot2(*positions.LEFT_PANEL_BBOX)
        img=cv2.imread("screenshot.bmp")
        img=enhance.replace_color_with_white(img, (169, 169, 169))
        img=enhance.replace_color_with_white(img, (122, 122, 122),)
        img=enhance.binarize(img, 150)
        cv2.imwrite("bin.png", img)
        for texts in recognize.extract_all_text_from_file("bin.png"):

            # if str(texts) in unused_texts:
            #     continue
            contains=False
            for s in unused_texts:
                if str(texts) in s or s in str(texts):
                    contains=True
                    break
            if contains: continue
            # print(texts)
            if texts in clicked:
                continue
            click(*texts.get_center(*positions.get_bbox_pos(positions.LEFT_PANEL_BBOX)))
            clicked.append(texts)
            sleep(0.1)
            imageWin.screenshot2(*positions.INFO_BBOX)
            result=extract_all_text_from_screenshot()
            if(len(result)==0):
                 continue
            user_name=result[0].text
            user_id=result[1].text.replace('QQ','').replace(' ','')
            imageWin.screenshot2(*positions.REMARKS_BBOX)
            result=extract_all_text_from_screenshot()
            user_displayname=recognize.get_key_value_vertical(result,"备注").text
            user_remark=recognize.get_key_value_vertical(result,"签名").text
            # contacts.append(structs.User(user_id,user_name,user_displayname,user_remark))
            r=structs.User(user_id,user_name,user_displayname,user_remark)
            if r not in contacts:
                contacts.append(r)
                db.save_user(r)
            print(contacts[-1])
            sleep(0.1)
    print(f'elapsed time: {time.time()-start_time}s')
    db.close()
    return contacts

def check_groups(timeout=60):
    db=sqlcontroller.GroupDatabase()
    db.delete_all()
    start_time=time.time()
    unused_texts, left_panel_pos = check_groups_first()
    contacts:List[structs.Group]=[]


    clicked=[]
    while not is_buttom(*positions.LEFT_PANEL_BBOX):
        if time.time()-start_time>timeout:
            break;
        btn=recognize.match_expand_buttons()
        for b in btn:
            click(left_panel_pos[0]+b[0],left_panel_pos[1]+b[1])
        imageWin.screenshot2(*positions.LEFT_PANEL_BBOX)
        # imageWin.screenshot2(*positions.LEFT_PANEL_BBOX)
        img=cv2.imread("screenshot.bmp")
        img=enhance.replace_color_with_white(img, (169, 169, 169))
        img=enhance.replace_color_with_white(img, (122, 122, 122),)
        img=enhance.binarize(img, 150)
        cv2.imwrite("bin.png", img)
        
        for texts in recognize.extract_all_text_from_file("bin.png"):
            contains=False
            for s in unused_texts:
                if str(texts) in s or s in str(texts):
                    contains=True
                    # break
            if contains: continue
            # print(texts)
            if texts in clicked:
                continue
            click(*texts.get_center(*positions.get_bbox_pos(positions.LEFT_PANEL_BBOX)))
            clicked.append(texts)
            print(texts)
            sleep(0.1)
            imageWin.screenshot2(*positions.INFO_BBOX)
            result=extract_all_text_from_screenshot()
            if(len(result)==0):
                 continue
            group_name=result[0].text
            group_id=result[1].text.replace('群号','').replace(' ','')
            imageWin.screenshot2(*positions.REMARKS_BBOX)
            r=structs.Group(group_id,group_name)
            if r not in contacts:
                contacts.append(r)
                db.save_group(r)
            print(contacts[-1])
            sleep(0.1)
    print(f'elapsed time: {time.time()-start_time}s')
    db.close()
    return contacts

def check_groups_first():
    start_time=time.time()

    click(*positions.CONTACT_BUTTON)
    unused_texts=['>']
    sleep(0.1)
    imageWin.screenshot(*positions.LEFT_PANEL_BBOX);
    left_panel_pos=positions.get_bbox_pos(positions.LEFT_PANEL_BBOX)
    click(positions.LEFT_PANEL_BBOX[2],positions.LEFT_PANEL_BBOX[3])
    scroll_down()
    imageWin.screenshot2(*positions.LEFT_PANEL_BBOX);
    sleep(0.1)
    for texts in extract_all_text_from_screenshot():
        unused_texts.append(str(texts))
        if "群聊" in texts.text:
            print(texts.bbox)
            sleep(1)
            click(*texts.get_center(*left_panel_pos))
            sleep(1)
    img=cv2.imread("screenshot.bmp")
    img=enhance.replace_color_with_white(img, (169, 169, 169))
    img=enhance.replace_color_with_white(img, (122, 122, 122),)
    img=enhance.binarize(img, 150)
    cv2.imwrite("bin.png", img)
    for texts in recognize.extract_all_text_from_file("bin.png"):
        if texts.text not in unused_texts:
            unused_texts.append(str(texts))
    print(unused_texts)
    click(positions.LEFT_PANEL_BBOX[2],positions.LEFT_PANEL_BBOX[3])
    return unused_texts,left_panel_pos


def get_users_in_groups(timeout=300):
    db=sqlcontroller.GroupMemberDatabase()
    db.delete_all()
    start_time=time.time()
    

    unused_texts,left_panel_pos = check_groups_first()
    clicked=[]
    checked_groups=[]

    while not is_buttom(*positions.LEFT_PANEL_BBOX):
        if time.time()-start_time>timeout:
            break;
        btn=recognize.match_expand_buttons()
        for b in btn:
            click(left_panel_pos[0]+b[0],left_panel_pos[1]+b[1])
            break
        imageWin.screenshot2(*positions.LEFT_PANEL_BBOX)
        # imageWin.screenshot2(*positions.LEFT_PANEL_BBOX)
        img=cv2.imread("screenshot.bmp")
        img=enhance.replace_color_with_white(img, (169, 169, 169))
        img=enhance.replace_color_with_white(img, (122, 122, 122),)
        img=enhance.binarize(img, 150)
        cv2.imwrite("bin.png", img)
        groupdb=sqlcontroller.GroupDatabase()
        groups=groupdb.get_all_groups()

        for texts in recognize.extract_all_text_from_file("bin.png"):
            contains=False
            for s in unused_texts:
                if str(texts) in s or s in str(texts):
                    contains=True
                    # break
            if contains: continue
            # print(texts)
            if texts in clicked:
                continue
            click(*texts.get_center(*positions.get_bbox_pos(positions.LEFT_PANEL_BBOX)))
            clicked.append(texts)
            print(texts)
            sleep(0.1)
            imageWin.screenshot2(*positions.INFO_BBOX)
            result=extract_all_text_from_screenshot()
            if(len(result)==0):
                 continue
            group_name=result[0].text
            if group_name in checked_groups:
                continue
            checked_groups.append(group_name)
            try:
                group_id=result[1].text.replace('群号','').replace(' ','')
            except IndexError as e:
                print(e)
                continue
            sg = structs.Group(group_id,group_name)
            if not sg in groups:
                groupdb.save_group(sg)
            # recognize.click_text("发消息")
            click(*positions.SEND_MESSAGE_BUTTON)
            sleep(1)
            userdb=sqlcontroller.UserDatabase()

            users=userdb.get_all_users()
            previous_result=[]
            click(*positions.get_bbox_pos_rev(positions.GROUP_MEMBER_BBOX))
            for i in range(30):
                imageWin.screenshot2(*positions.GROUP_MEMBER_BBOX)
                
                result=extract_all_text_from_screenshot()
                # input('press enter to continue...')
                
                
                for member in result:
                    m=structs.GroupMember(group_id=group_id,user_id="",card="",nickname=replace_right(member.text,"...",""))
                    in_previous=False
                    for previous_member in previous_result:
                        if (previous_member.text==member.text):
                            in_previous=True
                            break
                    if in_previous:
                        continue
                    for user in users:
                        if (user.user_name==m.nickname):
                            m.user_id=user.user_id
                            break
                    if m.user_id =="":
                        m.user_id=suid(m.nickname)
                        userdb.save_user(structs.User(m.user_id,m.nickname))
                        print(structs.User(m.user_id,m.nickname))
                    print(m)
                    
                    # db.save_member(m)
                    db.insert(m)
                
                for _ in range(2): scroll_down()
                at_bottom=True;
                for (member,previous_member) in zip(result,previous_result):
                    print(member.text,'-',previous_member.text)
                    if (member.text!=previous_member.text):
                        at_bottom=False;
                        break
                if len(result) ==0:
                    break
                if len(previous_result)==0:
                    at_bottom=False
                if (at_bottom):
                    break
                previous_result=result.copy()
                            

                
            click(*positions.CONTACT_BUTTON)
            sleep(0.2)
            recognize.click_text("群聊")
            btn=recognize.match_expand_buttons()
            for b in btn:
                click(left_panel_pos[0]+b[0],left_panel_pos[1]+b[1])
    print(f'time elapsed: {time.time()-start_time :.2f}s')

def replace_right(text,old,new):
    '''将最右边的old替换成new'''
    index=text.rfind(old)
    return text[:index]+new+text[index+len(old):]

def get_all_messages(timeout=300):
    start_time=time.time()
    click(*positions.CHAT_BUTTON)
    # imageWin.screenshot2(*positions.LEFT_PANEL_BBOX)
    sleep(0.5)
    click(*positions.get_bbox_pos_rev(positions.LEFT_PANEL_BBOX))
    collected=[]
    groupsdb=sqlcontroller.GroupDatabase()
    groups=groupsdb.get_all_groups()
    userdb=sqlcontroller.UserDatabase()
    users=userdb.get_all_users()
    db=sqlcontroller.PrivateMessageDB()
    in_collected_count=0
    while True:
        if in_collected_count ==positions.MAX_CONTACT_COUNT -1:
            return
        in_collected_count=0
        for i in range(positions.MAX_CONTACT_COUNT):
            print(f'{i+1} / {positions.MAX_CONTACT_COUNT}')
            if time.time() - start_time > timeout:
                return
            current_position=positions.START_DETECTING_MESSAGE_POS.copy()
            current_position[0]+=i*positions.DETECTING_MESSAGE_DELTA[0]
            current_position[1]+=i*positions.DETECTING_MESSAGE_DELTA[1]
            click(*current_position)
            # click()
            sleep(0.5)
            is_group=False
            imageWin.screenshot2(*positions.IS_GROUP_DETECT_BBOX)
            if recognize.contains("群聊",'screenshot.bmp'):
                is_group=True
            imageWin.screenshot2(*positions.TITLE_BBOX)
            texts = extract_all_text_from_screenshot()
            title=''.join([t.text for t in texts])
            if title in collected:
                in_collected_count+=1
                continue
            collected.append(title)
            mouse_move(*positions.START_DRAGGING)
            left_mouse_down()
            mouse_move(*positions.END_DRAGGING)
            sleep(10)
            left_mouse_up()
            imageWin.screenshot2(0,0,config.getint('general','width'),config.getint('general','height'))
            sleep(0.5)
            added=[]
            btn=recognize.match_copy_buttons()
            for b in btn:
                click(b[0],b[1])
            chatContents=conversationStyleExtract(pyperclip.paste())

            user_id=''
            if is_group:
                for group in groups:
                    if title in group.group_name or group.group_name in title:
                        user_id=group.group_id
                        break
            else:
                for user in users:
                    if title in user.user_name or user.user_name in title:
                        user_id=user.user_id
                        break
            if user_id=='':
                user_id=suid(title)
            

            
            for chatContent in chatContents:
                c=structs.PrivateMessage(message_type='group' if is_group else 'private', 
                                        message_id=suid(chatContent.text), user_id=user_id, message=chatContent.text, raw_message=""
                                        )

                message_added=False
                for message in added:
                    if c==message:
                        message_added=True
                        break
                if message_added:
                    continue
                added.append(c)
                db.insert(c)
                print(c)
        for _ in range(4): scroll_down()

            
def send_like_(user_id,repeat,timeout=120):
    start_time=time.time()
    db=sqlcontroller.UserDatabase()
    user=db.get_user(user_id)
    print(user)
    if user  is None:
        raise FileNotFoundError(f"用户{user_id}不存在")
    click(*positions.CONTACT_BUTTON)
    left_panel_pos=positions.get_bbox_pos(positions.LEFT_PANEL_BBOX)

    while True:
        if time.time()-start_time>timeout:
            raise TimeoutError(f"用户{user_id}在{timeout}秒内未找到")
        imageWin.screenshot2(*positions.LEFT_PANEL_BBOX)
        click_expend_buttons(left_panel_pos)
        imageWin.screenshot2(*positions.LEFT_PANEL_BBOX)
        if recognize.click_text(user.user_name) or recognize.click_text(user.user_displayname):
            for r in range(repeat):
                click(*positions.LIKE_BUTTON)
                sleep(0.2)
            return
        else:
            print(f"未找到用户{user_id}")
            click(*positions.get_bbox_pos_rev(positions.LEFT_PANEL_BBOX,[-50]*2))
            for _ in range(5): scroll_down()

def click_expend_buttons(left_panel_pos,only_once=False):

    btn=recognize.match_expand_buttons()
    if only_once:
        if(len(btn) ==0):
            return
        click(left_panel_pos[0]+btn[0][0],left_panel_pos[1]+btn[0][1])
        return
    for b in btn:
        click(left_panel_pos[0]+b[0],left_panel_pos[1]+b[1])

def send_message_(detail_type, detail_id, message,timeout=60):
    start_time=time.time()
    click(*positions.CHAT_BUTTON)
    click(*positions.CONTACT_BUTTON)
    click(*positions.get_bbox_pos_rev(positions.LEFT_PANEL_BBOX,[-50]*2))
    sleep(0.2)
    for _ in range(2): scroll_down()

    target=None
    target_string=''
    target_string2=''
    if(detail_type == "group"):
        recognize.click_text("群聊")
        db=sqlcontroller.GroupDatabase()
        target=db.get_group(detail_id)
    else:
        db=sqlcontroller.UserDatabase()
        target=db.get_user(detail_id)
    if not target:
        raise FileNotFoundError(f'{detail_type} {detail_id} not found')
    target_string=target.group_name if isinstance(target, sqlcontroller.Group) else target.user_name
    target_string2='' if isinstance(target, sqlcontroller.Group) else target.user_displayname

    imageWin.screenshot2(*positions.LEFT_PANEL_BBOX)
    left_panel_pos=positions.get_bbox_pos(positions.LEFT_PANEL_BBOX)
    while True:
        if time.time()-start_time>timeout:
            raise TimeoutError(f'timeout{timeout}')
        sleep(0.5)
        imageWin.screenshot2(*positions.LEFT_PANEL_BBOX)
        click_expend_buttons(left_panel_pos,True)
        sleep(0.5)
        if  (recognize.click_text(target_string) or recognize.click_text(target_string2)):

            # imageWin.screenshot2(0,0,config.getint('window','width'),config.getint('window','height'))
            success=recognize.click_text("发消息")
            # print(success)
            if success:
                break
        for _ in range(4) : scroll_down()
        imageWin.screenshot2(*positions.LEFT_PANEL_BBOX)
        click_expend_buttons(left_panel_pos,True)

    sleep(0.2)
    click(*positions.ENTER_MESSAGE)
    for text in message.split('\n'):
        pyperclip.copy(text)
        paste()
        press('enter')
        sleep(0.05)
    sleep(0.2)
    hotkey('ctrl','enter')
    print(f'elapsed :{time.time()-start_time :2f}s')
    return suid(message)


    

if __name__ == '__main__':
    # focus()
    imageWin.screenshot(0,0,1280,720)
    print(extract_all_text_from_screenshot())