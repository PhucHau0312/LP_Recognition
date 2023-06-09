
import cv2
import numpy as np
from lib_detection import load_model, detect_lp, im2single


def sort_contours(cnts):

    reverse = False
    i = 0
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))
    return cnts

char_list =  '0123456789ABCDEFGHKLMNPRSTUVXYZ'

def fine_tune(lp):
    newString = ""
    for i in range(len(lp)):
        if lp[i] in char_list:
            newString += lp[i]
    return newString

img_path = "test/test2.jpg"

wpod_net_path = "wpod-net_update1.json"
wpod_net = load_model(wpod_net_path)

Ivehicle = cv2.imread(img_path)

Dmax = 608
Dmin = 288

ratio = float(max(Ivehicle.shape[:2])) / min(Ivehicle.shape[:2])
side = int(ratio * Dmin)
bound_dim = min(side, Dmax)

_ , LpImg, lp_type = detect_lp(wpod_net, im2single(Ivehicle), bound_dim, lp_threshold=0.5)


digit_w = 30 
digit_h = 60 

model_svm = cv2.ml.SVM_load('svm.xml')

if (len(LpImg)):

    LpImg[0] = cv2.convertScaleAbs(LpImg[0], alpha=(255.0))
    roi = LpImg[0]

    gray = cv2.cvtColor( LpImg[0], cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 127, 255,
                         cv2.THRESH_BINARY_INV)[1]

    cv2.imshow("Anh bien so sau threshold", binary)
    cv2.waitKey()

    kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thre_mor = cv2.morphologyEx(binary, cv2.MORPH_DILATE, kernel3)
    cont, _  = cv2.findContours(thre_mor, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)


    plate_info = ""

    for c in sort_contours(cont):
        (x, y, w, h) = cv2.boundingRect(c)
        ratio = h/w
        if 1.5<=ratio<=3.5: 
            if h/roi.shape[0]>=0.6: 
                cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

                curr_num = thre_mor[y:y+h,x:x+w]
                curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
                _, curr_num = cv2.threshold(curr_num, 30, 255, cv2.THRESH_BINARY)
                curr_num = np.array(curr_num,dtype=np.float32)
                curr_num = curr_num.reshape(-1, digit_w * digit_h)

                result = model_svm.predict(curr_num)[1]
                result = int(result[0, 0])

                if result<=9: 
                    result = str(result)
                else: 
                    result = chr(result)

                plate_info +=result

    cv2.imshow("Cac contour tim duoc", roi)
    cv2.waitKey()

    cv2.putText(Ivehicle,fine_tune(plate_info),(50, 50), cv2.FONT_HERSHEY_PLAIN, 3.0, (0, 0, 255), lineType=cv2.LINE_AA)

    print("Bien so=", plate_info)
    cv2.imshow("Hinh anh output",Ivehicle)
    cv2.imwrite('result/test2.png', Ivehicle)
    cv2.waitKey()
cv2.destroyAllWindows()
