import cv2
import sys
import pyocr
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image,ImageEnhance     
cap = cv2.VideoCapture('target/111.mp4')       

# openCV　動画生成
# w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
# h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
# fps = cap.get(cv2.CAP_PROP_FPS)
# avi =  cv2.VideoWriter_fourcc('X', 'V', 'I', 'D') #defualt
# writer = cv2.VideoWriter('resultt.avi',avi, int(fps), (int(h), int(w)))

# pyocr
tools = pyocr.get_available_tools()
# ここ使っているのOCR toolはtesseract-ocr
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
tool = tools[0]
builder = pyocr.builders.TextBuilder()
#言語設定
langs = tool.get_available_languages()
lang_jpn = langs[2]
lang_eng = langs[1]
print("Will use language: '%s' and '%s'" %(lang_jpn,lang_eng))

count = 1
frequency = 45 # screenshotの間隔 60:2s
number = 1

name_list = [] # 学籍番号だけ
fullname_list = [] #学籍番号＋名前
time_list = [] #発言時間
explode = [] #円グラフを描く時の距離

with open("test.txt","w") as clear:
                clear.write('')
                
while (cap.isOpened()):
        success, frame = cap.read()
        # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE) 
        while success: 
            # cv2.imshow("demo", frame)
            success, frame = cap.read()
            if count % frequency == 0:
                frame=frame[10:80,100:900]
                with open("test.txt","a") as f:
                    if(cv2.imwrite('pic/'+str(number)+ '.png',frame)):
                        im = Image.open('pic/'+str(number)+ '.png')
                        #画像を拡大することで認識精度が向上するようです
                        im = im.resize((im.width * 4, im.height * 4))
                        # 二値化
                        im = im.convert('L')
                        # コントラストの強化
                        sharpness = ImageEnhance.Contrast(im)
                        im = sharpness.enhance(1.5)
                        # 日本語を認識する際に時間を正確に認識できないため、両者を分離している
                        name = im.transform((2000, 280), Image.EXTENT, (600, 0, 2600, 280))
                        time = im.transform((600, 280), Image.EXTENT, (2600, 0, 3200, 280))
                        name.save('pic/'+'name'+str(number)+ '.png')
                        #もう一度コントラストの強化
                        sharpness = ImageEnhance.Contrast(time)
                        time = sharpness.enhance(1.5)
                        time.save('pic/'+'time'+str(number)+ '.png')
                        # 日本語を認識
                        txt_jpn = tool.image_to_string(
                            name,
                            lang_jpn,
                            builder
                            )
                        # 時間を認識
                        txt_eng = tool.image_to_string(
                            time,
                            lang_eng,
                            builder
                            )

                        i = 0
                        aa = '①②③④⑤⑥⑦⑧⑨' # 識別の時「②6001⑧04②⑧5」場合がある
                        
                        if(txt_jpn):
                            # 学籍番号の記号を数字に変換する
                            while(txt_jpn[i]):
                                if(txt_jpn[i] in aa):
                                    num = aa.find(txt_jpn[i]) + 1
                                    txt_jpn = txt_jpn[:i] + str(num) + txt_jpn[i+1:]
                                if(i>=10):
                                    break
                                i += 1
                            # listに追加
                            if(txt_jpn[:11]) not in name_list :
                                # name = im.convert('1')
                                # plt.imshow(name)
                                # plt.pause(1) 
                                # plt.close() 
                                name_list.append(txt_jpn[:11])
                                find_ga = txt_jpn.find('が')
                                fullname_list.append(txt_jpn[:find_ga])
                                time_list.append(1.5)
                                explode.append(0.02)
                            else:
                                time_number = name_list.index(txt_jpn[:11])
                                time_list[time_number] += 1.5
                                                       
                        f.write(txt_eng + ':' + txt_jpn + '\n' )                        
                    print(txt_jpn,txt_eng)
                    print('-------------------------------------')
                    number += 1
            count += 1
            # writer.write(frame)
            if (cv2.waitKey(20) & 0xff) == ord('q'): 
                break
        cap.release()
        dict1 = dict(zip(fullname_list,time_list))
        print(dict1)
        
        # 円グラフを描く
        fig = plt.figure(figsize=(8,8))
        fig.canvas.set_window_title('発言時間の割合')
        plt.pie(time_list,explode=explode,labels=fullname_list,autopct='%1.1f%%')
        plt.title('')
        plt.savefig('./発言時間の割合')
        plt.show()
        if (cv2.waitKey(20) & 0xff) == ord('q'): 
            break
# writer.release()
cv2.destroyAllWindows()
cv2.waitKey(1)
