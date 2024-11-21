import gradio as gr
import os
from tools.data_preprocess import data_preprocess
import os
import V2EM_prediction.main_for_st
import numpy as np
import shutil

def mseva(video,audio,script):
    avi_path="V2EM_prediction/temp/video.mp4"
    wav_path="V2EM_prediction/temp/audio.wav"
    csv_path="V2EM_prediction/temp/script.csv" 
    shutil.copy(video.name,avi_path)
    shutil.copy(audio.name,wav_path)
    shutil.copy(script.name,csv_path)
    data_preprocess()
    V2EM_prediction.main_for_st.emotion_analysis()
    emotion_list=[]
    with open('result.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip('\n')
            emotion_list.append(line)
        print(emotion_list)
    emotion_key = ['生气', '反感', '害怕', '高兴', '悲伤', '惊讶']  # mosei
    #显示视频情绪极性
    emotion_category=emotion_key[np.argmax(emotion_list)]
    negative=['生气','反感','害怕','悲伤']
    positive=['高兴','激动']
    emotion=''
    if emotion_category in positive:
        emotion='积极'
    elif emotion_category in negative:
        emotion='消极'
    else:
        emotion='中立'
    return emotion,emotion_category

def upload(file):
    print(file.name)
    return file.name


demo = gr.Interface(
    fn=mseva,
    inputs=[
        gr.components.File(label="Short(mp4)", file_types=[".mp4"]),
        gr.components.File(label="Audio(wav)", file_types=[".wav"]),
        gr.components.File(label="Script(csv)", file_types=[".csv"]),
    ],
    outputs=[gr.Text(label="Emotion"),
             gr.Text(label="Emotion Category"),
    ]
)

if __name__=="__main__":
    demo.launch(server_name="0.0.0.0",share=True,inbrowser=True)