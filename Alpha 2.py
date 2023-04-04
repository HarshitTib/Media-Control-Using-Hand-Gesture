import cv2
import mediapipe as mp
import pyautogui
import time

# To detect the hand
# for idx, hand_handedness in enumerate(results.multi_handedness):
    # print(hand_handedness.classification)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
flag_right = 0
flag_left = 0
tipIds = [4, 8, 12, 16, 20]
state = "work"
stateMin = "work"
stateSleep = "work"
Gesture = None
sc = 0

pTime = 0
lr = []
totalFingers = []

# Himanshu start

def fingersUp(ls):
    indices = [8, 12, 16, 20]
    ans = [0, 0, 0, 0, 0]
    count = 1
    for i in indices:
        if(ls[i][2] < (ls[i-3][2] - 70)):
            ans[count] = 1
        count += 1
    if ls[4][1] < ls[2][1]:
        ans[0] = 1
    return ans    
        

def handStraight(ls):
    indices = [0, 8, 12, 16, 20]
    ans = [0, 0, 0, 0, 0]
    count = 0
    for idx, hand_handedness in enumerate(results.multi_handedness):
            x = hand_handedness.classification[0].label
    for i in range(0, len(indices) - 1):
        if x == 'Right':
            if ls[i][1] < ls[i+1][1]:
                return False
            return True
        if x == 'Left':
            if ls[i][1] > ls[i+1][1]:
                return False
            return True
        return True

# Himanshu stop

def fingerPosition(image, handNo=0):
    lmList = []
    if results.multi_hand_landmarks:
        myHand = results.multi_hand_landmarks[handNo]
        for id, lm in enumerate(myHand.landmark):
            h, w, c = image.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append([id, cx, cy])
    return lmList

cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    min_detection_confidence=0.8,
    min_tracking_confidence=0.5) as hands:

  while cap.isOpened():

    success, image = cap.read()
 
    if not success:
        print("Ignoring empty camera frame.")
        continue

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(image, f'FPS:{int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:

      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    lmList = fingerPosition(image)

    if len(lmList) != 0:
        
        
        # harshit next track

        fingers = []
        # finding the coordinate of x in middle finger and thumb for their right movement (lmList[12][1] < lmList[4][1])
        # finding the difference between thumb and index finger for some error abs(lmList[4][2] - lmList[5][2]) > 40
        # finding the coordinate of y in middle finger and thumb for the thumb to point in the upward direction (lmList[4][2] < lmList[12][2])
        if((lmList[12][1] < lmList[4][1]) and abs(lmList[4][2] - lmList[5][2]) > 40 and lmList[4][2] < lmList[12][2]):
            for id in range(1, 4):
                y1 = lmList[tipIds[id]][2]-lmList[tipIds[id] - 3][2] 
                x1 = lmList[tipIds[id]][1]-lmList[tipIds[id] - 3][1]
                if(x1!=0):
                    m = y1/x1 #finding the slop of each finger
                    if (m < 0.3 and m > -0.3): # setting the threshold
                        fingers.append(1)
            totalFingers = fingers.count(1)
            if (flag_right == 0 and totalFingers == 3):
                flag_right = 1
                pyautogui.press('nexttrack')
                # print('next track')
        else:
            flag_right = 0
                
        # end next track
       
       # harshit prev track
       
        # finding the coordinate of x in middle finger and thumb for their left movement (lmList[12][1] > lmList[4][1])
        # finding the difference between thumb and index finger for some error abs(lmList[4][2] - lmList[5][2]) > 40
        # finding the coordinate of y in middle finger and thumb for the thumb to point in the downward direction (lmList[4][2] > lmList[12][2])
        fingers = []
        if((lmList[12][1] > lmList[4][1]) and abs(lmList[4][2] - lmList[5][2]) > 40 and (lmList[4][2] > lmList[12][2])):
            for id in range(1, 4):
                y1 = lmList[tipIds[id]][2]-lmList[tipIds[id] - 3][2]
                x1 = lmList[tipIds[id]][1]-lmList[tipIds[id] - 3][1]
                if(x1!=0):
                    m = y1/x1 #finding the slop of each finger
                    if (m < 0.3 and m > -0.3): #setting the threshold 
                        fingers.append(1)
            totalFingers = fingers.count(1)
            if (flag_left == 0 and totalFingers == 3):
                flag_left = 1
                pyautogui.press('prevtrack')
                # print('prev track')
        else:
            flag_left = 0
            
        #end prev track


        # Minimize Himanshu's implementation
        
        fingers = []
        fingers = fingersUp(lmList)
        totalFingers = fingers.count(1)
        conditionForMin = stateMin == "work" and handStraight(lmList) and totalFingers == 2 and fingers[0] == 1 and fingers[4] == 1; 
        yCoordinatesOfFingers = min(lmList[16][2], lmList[12][2], lmList[8][2])
        if conditionForMin and lmList[20][2] < yCoordinatesOfFingers and lmList[4][2] < yCoordinatesOfFingers:
            stateMin = "rest"
            pyautogui.hotkey('winleft', 'd')
            # print('minimize')
            
      
        if stateMin == "rest" and (totalFingers == 5 or totalFingers == 0):
            stateMin = "work"

        # Minimize Himanshu's implementation over

        #window minimize
        
        # Himanshu start play pause
        
        fingers = []
        fingers = fingersUp(lmList)
        totalFingers = fingers.count(1)
        for idx, hand_handedness in enumerate(results.multi_handedness):
            handName = hand_handedness.classification[0].label
       
        if state == "work" and handName=='Right' and lmList[4][1] > lmList[8][1] and totalFingers == 2 and fingers[2] == 1 and fingers[1] == 1:
            state = "rest"
            pyautogui.press('playpause')
            # print('play pause')
      
        if state == "rest" and (totalFingers == 5 or totalFingers == 0):
            state = "work"
         
        # Himanshu stop play pause

        # Himanshu start sleep

        # fingers = []
        # fingers = fingersUp(lmList)
        # totalFingers = fingers.count(1)
        # for idx, hand_handedness in enumerate(results.multi_handedness):
        #     handName = hand_handedness.classification[0].label
        # print(fingers)
        # if stateSleep == "work" and handName == 'Left' and handStraight(lmList) and lmList[20][1] < lmList[8][1] and totalFingers == 3 and fingers[0] == 1 and fingers[4] == 1 and fingers[3] == 1:
        #     print('sleep', sc)
        #     sc += 1
        #     # pyautogui.press('sleep')
      
        # if stateSleep == "rest" and (totalFingers == 5 or totalFingers == 0):
        #     stateSleep = "work"

        # Himanshu stop sleep


    cv2.imshow("Media Controller", image)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord("q"):
        break
  
  cv2.destroyAllWindows()

# import pyautogui
# print(pyautogui.KEYBOARD_KEYS)