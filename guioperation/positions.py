from typing import List,Tuple,Any


CONTACT_BUTTON=[27,103]
CHAT_BUTTON=[27,62]
LEFT_PANEL_BBOX=[62,87,241,629]
SEND_MESSAGE_BUTTON=[839,677]
LIKE_BUTTON=[1033,164]

ENTER_MESSAGE=[670,612]

START_DETECTING_MESSAGE_POS=[62,99]
DETECTING_MESSAGE_DELTA=[0,65]
MAX_CONTACT_COUNT=10

START_DRAGGING=[1067,490]
END_DRAGGING=[326,1]

INFO_BBOX=[641,119,374,97]
REMARKS_BBOX=[533,328,503,135]
GROUP_MEMBER_BBOX=[1101,188,128,518]

TITLE_BBOX=[319,56,716,25]
IS_GROUP_DETECT_BBOX=[1101,158,65,31]



def get_bbox_pos(bbox,dv:List[int]=[0,0]) -> Tuple[int,int]:
    return bbox[0]+dv[0],bbox[1]+dv[1]
def get_bbox_pos_rev(bbox,dv:List[int]=[0,0]) -> Tuple[int,int]:
    return bbox[0]+bbox[2]+dv[0],bbox[1]+bbox[3]+dv[1]