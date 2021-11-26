import cv2 as cv
import numpy as np
import mediapipe as mp
from collections import Counter
from collections import deque

import csv
import copy
import autopy
import os

import app as detector
# import osu

from utils import CvFpsCalc
from model import KeyPointClassifier
from model import PointHistoryClassifier

######## OSU ##############
import turtle
import random


##################################################################
args = detector.get_args()

cap_device = args.device
cap_width = args.width
cap_height = args.height

use_static_image_mode = args.use_static_image_mode
min_detection_confidence = args.min_detection_confidence
min_tracking_confidence = args.min_tracking_confidence

use_brect = True

###############################################################
cap = cv.VideoCapture(cap_device)
cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

#############################################################
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=use_static_image_mode,
    max_num_hands=1,
    min_detection_confidence=min_detection_confidence,
    min_tracking_confidence=min_tracking_confidence,
)
keypoint_classifier = KeyPointClassifier()

point_history_classifier = PointHistoryClassifier()

###########################################################
with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
    keypoint_classifier_labels = csv.reader(f)
    keypoint_classifier_labels = [
        row[0] for row in keypoint_classifier_labels
    ]
with open(
    'model/point_history_classifier/point_history_classifier_label.csv',
        encoding='utf-8-sig') as f:
    point_history_classifier_labels = csv.reader(f)
    point_history_classifier_labels = [
        row[0] for row in point_history_classifier_labels
    ]

#########################################################
cvFpsCalc = CvFpsCalc(buffer_len=10)

#################################################################
history_length = 16
point_history = deque(maxlen=history_length)

################################################
finger_gesture_history = deque(maxlen=history_length)

########################################################################
mode = 0 
tmp_path = 0 
tmp_rename = 0 
images_path = 'tmp_images/'
wScr, hScr = autopy.screen.size()

# while True:
def detect_gesture(mode):
    ############## before loop #########
    fps = cvFpsCalc.get()

    # キー処理(ESC：終了) #################################################
    key = cv.waitKey(10)
    # if key == 27:  # ESC
    #     break
    number, mode = detector.select_mode(key, mode)

    # カメラキャプチャ #####################################################
    ret, image = cap.read()
    if not ret:
        print('Failed to capture image')
        return
    image = cv.flip(image, 1)  # ミラー表示
    debug_image = copy.deepcopy(image)

    # 検出実施 #############################################################
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True

    #  ####################################################################
    if results.multi_hand_landmarks is not None:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                              results.multi_handedness):
            # 外接矩形の計算
            brect = detector.calc_bounding_rect(debug_image, hand_landmarks)
            # ランドマークの計算
            landmark_list = detector.calc_landmark_list(debug_image, hand_landmarks)

            # 相対座標・正規化座標への変換
            pre_processed_landmark_list = detector.pre_process_landmark(
                landmark_list)
            pre_processed_point_history_list = detector.pre_process_point_history(
                debug_image, point_history)
            # 学習データ保存
            detector.logging_csv(number, mode, pre_processed_landmark_list,
                        pre_processed_point_history_list)

            # ハンドサイン分類
            hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
            if hand_sign_id == 2:  # 指差しサイン
                point_history.append(landmark_list[8])  # 人差指座標
            else:
                point_history.append([0, 0])

            # フィンガージェスチャー分類
            finger_gesture_id = 0
            point_history_len = len(pre_processed_point_history_list)
            if point_history_len == (history_length * 2):
                finger_gesture_id = point_history_classifier(
                    pre_processed_point_history_list)

            # 直近検出の中で最多のジェスチャーIDを算出
            finger_gesture_history.append(finger_gesture_id)
            most_common_fg_id = detector.Counter(
                finger_gesture_history).most_common()
            
            if(keypoint_classifier_labels[hand_sign_id] == 'Close'):
                autopy.mouse.click()
            
            pos_x = (landmark_list[2][0] + landmark_list[0][0]) /2#(brect[0] + brect[2])/2
            pos_y = (landmark_list[2][1] + landmark_list[0][1]) /2#(brect[1] + brect[3])/2
            if(pos_x < wScr and pos_y < hScr and pos_x > 0 and pos_y > 0):
                autopy.mouse.move( pos_x, pos_y)
                # autopy.mouse.move(int(landmark_list[8][0]), int(landmark_list[8][1]))
            # Box
            # debug_image = detector.draw_bounding_rect(use_brect, debug_image, brect)
            # esqueleto hand
            debug_image = detector.draw_landmarks(debug_image, landmark_list)
            # debug_image = draw_info_text(
            #     debug_image,
            #     brect,
            #     handedness,
            #     keypoint_classifier_labels[hand_sign_id],# close or open hand
            #     point_history_classifier_labels[most_common_fg_id[0][0]],
            # )
    else:
        point_history.append([0, 0])
    # puntero
    debug_image = detector.draw_point_history(debug_image, point_history)
    # debug_image = draw_info(debug_image, fps, mode, number)

    # display image #####################################################
    # cv.imshow('Hand Gesture Recognition', debug_image)
    path = images_path + str(tmp_path) + '.png'
    cv.imwrite(path,debug_image)

# cap.release()
# cv.destroyAllWindows()

def setup():
    s=turtle.Screen()
    t=turtle.Turtle()
    s.setup(1.0,1.0,None,None)
    t.hideturtle()
    t.up()
    t.speed(0)
    turtle.tracer(0,0)
    return s,t

def drawCSq(t,cx,cy,a):
    t.goto(cx-(a/2),cy-(a/2))
    t.down()
    t.goto(cx+(a/2),cy-(a/2))
    t.goto(cx+(a/2),cy+(a/2))
    t.goto(cx-(a/2),cy+(a/2))
    t.goto(cx-(a/2),cy-(a/2))
    t.up()

def timer():
    global tstep
    global sx
    global sy
    global lastSpawn
    global Delay
    global HP
    global Score
    global Combo
    global tmp_path 

    if tstep>=lastSpawn+Delay:
        sx.append(random.randrange(-320+A,320-A))
        sy.append(random.randrange(-240+A,240-A))
        st.append(tstep)
        sttl.append(TTL)
        lastSpawn=tstep
        Delay-=max(1,Delay//DelayDecFact)
        Delay=max(MinDelay,Delay)

    j=0
    while j<len(sx):
        if(st[j]+sttl[j]<tstep):
            del st[j]
            del sttl[j]
            del sx[j]
            del sy[j]
            HP-=HpDec
            HP=max(0,HP)
            Combo=0
            print("HP:",HP,"Score:",Score,"Combo:",Combo,"Last Hit:",0)
        else:
            j+=1

    t.clear()

    for i in range(len(sx)):
        drawCSq(t,sx[i],sy[i],A)
        A2=A*((sttl[i]+st[i]-tstep-(sttl[i]*JudgmentLine))/sttl[i])
        if(A2>0):
            drawCSq(t,sx[i],sy[i],A+A2)
    detect_gesture(mode)
    # os.system("mv temp.png temp.gif")
    
    path_bg = images_path + str(tmp_path) + '.png'
    
    s.bgpic(path_bg)
    s.update()
    rm_command = "rm " + images_path + str(tmp_path) + '.png'
    os.system(rm_command)
    tmp_path = (tmp_path + 1)
    tstep+=1
    if HP>0:
        s.ontimer(timer,10)
    else:
        s.bye()

def click(x,y):
    global TTL
    global HP
    global Score
    global Combo

    if len(sx)>0 and sx[0]-(A/2)<x and sx[0]+(A/2)>x and sy[0]-(A/2)<y and sy[0]+(A/2)>y:
        TTL-=TTLDec
        TTL=max(MinTTL,TTL)
        HP+=HpInc
        HP=min(100,HP)
        Combo+=1
        HitDiff=abs((st[0]+(sttl[0]*(1-JudgmentLine)))-tstep)
        HitDiffPre=1-(HitDiff/(sttl[0]*(1-JudgmentLine)))
        LastHit=50+int(250*HitDiffPre)
        Score+=Combo*LastHit
        print("HP:",HP,"Score:",Score,"Combo:",Combo,"Last Hit:",LastHit)
        del sx[0]
        del sy[0]
        del st[0]
        del sttl[0]

    t.clear()

    for i in range(len(sx)):
        drawCSq(t,sx[i],sy[i],A)
        A2=A*((sttl[i]+st[i]-tstep-(sttl[i]*JudgmentLine))/sttl[i])
        if(A2>0):
            drawCSq(t,sx[i],sy[i],A+A2)

    s.update()

s,t=setup()
tstep=0
A=100
# time for respawn the square
Delay=50
TTL=100
DelayDecFact=15
TTLDec=5
MinDelay=30
MinTTL=45
JudgmentLine=0.33
lastSpawn=0
HP=100
Score=0
HpDec=5
HpInc=1
Combo=0
sx=[]
sy=[]
st=[]
sttl=[]

s.ontimer(timer,5)
s.onclick(click)

s.mainloop()