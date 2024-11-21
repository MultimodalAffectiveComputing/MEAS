import os
import subprocess
import time
import cv2
from ffmpy import FFmpeg
import ffmpeg


def data_preprocess():

    path='V2EM_prediction/temp/video.mp4'
    savepath='V2EM_prediction/temp/video_processed.avi'
    cap=cv2.VideoCapture(path)
    success, vid1 = cap.read()
    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height=int((cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    videowriter=None
    o_width=72
    o_height=128
    if(width>475 and width<485 and height>555 and height<565):
        o_width=180
        o_height=224

    elif(width>850 and width<855 and height>475 and height<485):
        #214 120
        o_width=214
        o_height=120
        
    elif (width > 475  and  width < 485  and  height > 845  and  height < 855):
        o_width=120
        o_height=214
    elif(width > 1070  and  width < 1090  and  height > 1910  and  height < 1930):
        #144 216
        o_width=144
        o_height=216
    
    s, img1 = cap.read()
    videowriter = cv2.VideoWriter(savepath, cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'), 25, (o_width,o_height))
    while s:
        try:
            _, img1 = cap.read()
            vid = cv2.resize(img1, (o_width, o_height), interpolation=cv2.INTER_LINEAR)
            videowriter.write(vid)
        except:
            break


# #转音频
#  n=n+1
#  ffmpeg_audio_string='ffmpeg -i E:\\dataset_marked_1\\audio\\{0}.mp3 -f wav  E:\\dataset_marked_1_preprocessed\\audio\\{1}.wav'.format(n,n)
#  p=subprocess.Popen(ffmpeg_audio_string,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#  p.wait()