# -*- coding:utf-8 -*-
# @Author: Shawnie
# @Time: 2022-11-26 19:45
# @File: test.py
import streamlit as st
import pandas as pd
from pyecharts.charts import Bar
from pyecharts.charts import Map
from pyecharts.faker import Faker
import streamlit_echarts
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from streamlit_echarts import st_echarts
from streamlit_echarts import st_pyecharts
from streamlit.components.v1 import html
# import emotion_analysis.main as main
import draw
#
import V2EM_prediction.main_for_st
from streamlit_echarts import st_echarts
import numpy as np
from tools.data_preprocess import data_preprocess
import os

side_bar = st.sidebar.radio(
    '语言/language',
    ['中文','English']
)  # 侧边栏

if 'stage' not in st.session_state:
    st.session_state.stage=0

if side_bar=='中文':

    choice=st.selectbox('分析',['短视频情感分析-演示','情感分析-视频音频文本单独上传'])

   

    if choice=='短视频情感分析-演示':#result.txt，result_modality.csv
        uploaded_file = st.file_uploader('请上传短视频视频')
        if uploaded_file is not None:
            st.success('成功！')
            fn = uploaded_file.name.split('.')[0]
            mp4_path = f'mp4/{fn}.mp4'
            st.video(mp4_path)

        btn_ea = st.button('情感分析')

        if btn_ea:
            fn = uploaded_file.name.split('.')[0]
            V2EM_prediction.main_for_st.emotion_analysis(str(fn))

            emotion_list = []
            with open('result.txt', 'r') as f:
                for line in f.readlines():
                    line = line.strip('\n')
                    emotion_list.append(line)
            print(emotion_list)
            # emotion_key = ['angry', 'excited', 'frustrated', 'happy', 'neutral', 'sad']#iemocap
            # emotion_key = ['生气', '激动', '沮丧', '高兴', '中立', '伤心']#iemocap
            #emotion_key = ['angry', 'disgusted', 'fear', 'happy', 'sad', 'surprise']  # mosei
            emotion_key = ['生气', '反感', '害怕', '高兴', '悲伤', '惊讶']  # mosei
            #显示视频情绪极性
            max_emotion=emotion_key[np.argmax(emotion_list)]
            negative=['生气','害怕','反感','悲伤']
            positive=['高兴','惊讶']
            if max_emotion in positive:
                st.write('该视频情绪是积极的')##显示语言
            elif max_emotion in negative:
                st.write('该视频情绪是消极的')#显示语言
            else:
                st.write('该视频情绪是中立的')#显示语言

            option = {'grid': {'top': 10, 'left': 50, 'right': 50, 'bottom': 50},
                    'tooltip': {'trigger': 'axis', 'confine': 'true'},
                    'yAxis': {'triggerEvent': 'true', 'data': emotion_key},
                    'xAxis': {},
                    'series': [{'name': 'emotion', 'type': 'bar', 'data': emotion_list,
                                'itemStyle': {'normal': {
                                    'label': {
                                        'show': 'true',
                                        'position': 'right',
                                        'textStyle': {'color': 'black'}
                                    }
                                }}}]
                    }
            st_echarts(options=option, height='500px', width='700px')

            # modality emotion
            data = pd.read_csv('result_modality.csv', encoding='utf-8', sep=';')
            option = {  # 提示框，鼠标悬浮交互时的信息提示
                'title': {'text': ' 单模态分析结果'},
                'tooltip': {'show': 'true',  # 是否显示
                            'trigger': 'axis',  # 触发类型，默认数据触发，见下图，可选为：'item' | 'axis'
                            'axisPointer': {
                                'type': 'shadow'
                            }
                            },
                'legend': {},
                'grid': {
                    'left': '3%',
                    'right': '4%',
                    'bottom': '3%',
                    'containLabel': 'true'
                },
                'xAxis': {
                    'type': 'value'
                },
                'yAxis': {
                    'type': 'category',
                    'data': [' 文本', '视频', '音频']
                },
                'series': [
                    {
                        'name': '生气',
                        'type': 'bar',
                        'stack': 'total',
                        'label': {
                            'show': 'true'
                        },
                        'emphasis': {
                            'focus': 'series'
                        },
                        'data': [float(data['angry'][i]) for i in range(3)]
                    },
                    {
                        'name': '反感',
                        'type': 'bar',
                        'stack': 'total',
                        'label': {
                            'show': 'true'
                        },
                        'emphasis': {
                            'focus': 'series'
                        },
                        'data': [float(data['disgusted'][i]) for i in range(3)]
                    },
                    {
                        'name': '沮丧',
                        'type': 'bar',
                        'stack': 'total',
                        'label': {
                            'show': 'true'
                        },
                        'emphasis': {
                            'focus': 'series'
                        },
                        'data': [float(data['fear'][i]) for i in range(3)]
                    },
                    {
                        'name': '高兴',
                        'type': 'bar',
                        'stack': 'total',
                        'label': {
                            'show': 'true'
                        },
                        'emphasis': {
                            'focus': 'series'
                        },
                        'data': [float(data['happy'][i]) for i in range(3)]
                    },
                    {
                        'name': '悲伤',
                        'type': 'bar',
                        'stack': 'total',
                        'label': {
                            'show': 'true'
                        },
                        'emphasis': {
                            'focus': 'series'
                        },
                        'data': [float(data['sad'][i]) for i in range(3)]
                    },
                    {
                        'name': '惊讶',
                        'type': 'bar',
                        'stack': 'total',
                        'label': {
                            'show': 'true'
                        },
                        'emphasis': {
                            'focus': 'series'
                        },
                        'data': [float(data['surprise'][i]) for i in range(3)]
                    }

                ]
            }
            st_echarts(options=option, height='500px')

    #视频分句情感波动图
            clips_num=0
            emotion_clip_list=[]
            with open('result_clip_1.txt','r') as f:
                for line in f.readlines():
                    line=line.strip()
                    line=line.split('\t')
                    line=list(map(float,line))
                    emotion_clip_list.append(line)
            for i in range(len(emotion_clip_list)):
                emotion_clip_list[i]=np.argmax(emotion_clip_list[i])
            print(emotion_clip_list)
            option={'title':{'text':'视频情感波动图'},
                    'xAxis':{'type':'category','data':[f'{i}_分片' for i in range(len(emotion_clip_list))]},
                    'yAxis':{'name':'情感分类','type': 'value' , 'data':[i for i in range(len(emotion_key))]},
                    'tooltip':{'show':'true',
                                'trigger':'axis'},
                    'series':[{'name':'视频情感波动曲线','type':'line','data':[int(i) for i in emotion_clip_list]}]
                    }
            st_echarts(options=option,height='500px')
            st.write('情感类型： 0--生气 1--反感 2--沮丧 3--高兴 4--悲伤 5--惊讶')


    if choice=='情感分析-视频音频文本单独上传':#result.txt，result_modality.csv
            uploaded_file_avi = st.file_uploader('请上传短视频视频(mp4)',type='mp4')
            uploaded_file_wav = st.file_uploader('请上传短视频音频(wav)',type='wav')
            uploaded_file_csv = st.file_uploader('请上传短视频字幕文件(csv)',type='csv')
            avi_path="V2EM_prediction/temp/video.mp4"
            wav_path="V2EM_prediction/temp/audio.wav"
            csv_path="V2EM_prediction/temp/script.csv"
            if uploaded_file_avi is not None and (not os.path.exists(avi_path)) and st.session_state.stage==0:
                st.success('上传视频文件成功！')
                fp = open(avi_path,mode="wb")
                fp.write(uploaded_file_avi.getvalue())
                fp.close()
                st.session_state.stage=1
                data_preprocess()
            if uploaded_file_wav is not None and (not os.path.exists(wav_path)) and st.session_state.stage==1:
                st.success('上传音频文件成功！')
                fp = open(wav_path,mode="wb")
                fp.write(uploaded_file_wav.getvalue())
                fp.close()
                st.session_state.stage=2
            if uploaded_file_csv is not None and (not os.path.exists(csv_path)) and st.session_state.stage==2:
                st.success('上传字幕文件成功！')
                fp = open(csv_path,mode="wb")
                fp.write(uploaded_file_csv.getvalue())
                fp.close()
                st.session_state.stage=3
        
            if uploaded_file_avi == None and uploaded_file_wav == None and uploaded_file_csv == None and st.session_state.stage==3:
                os.remove(avi_path)
                os.remove('V2EM_prediction/temp/video_processed.avi')
                os.remove(wav_path)
                os.remove(csv_path)
                st.session_state.stage=0
                
            
            btn_ea = st.button('情感分析')

            if btn_ea:
                V2EM_prediction.main_for_st.emotion_analysis()

                emotion_list = []
                with open('result.txt', 'r') as f:
                    for line in f.readlines():
                        line = line.strip('\n')
                        emotion_list.append(line)
                print(emotion_list)
                # emotion_key = ['angry', 'excited', 'frustrated', 'happy', 'neutral', 'sad']#iemocap
                # emotion_key = ['生气', '激动', '沮丧', '高兴', '中立', '伤心']#iemocap
                #emotion_key = ['angry', 'disgusted', 'fear', 'happy', 'sad', 'surprise']  # mosei
                emotion_key = ['生气', '反感', '害怕', '高兴', '悲伤', '惊讶']  # mosei
                #显示视频情绪极性
                max_emotion=emotion_key[np.argmax(emotion_list)]
                negative=['生气','反感','害怕','悲伤']
                positive=['高兴','惊讶']
                if max_emotion in positive:
                    st.write('该视频情绪是积极的')##显示语言
                elif max_emotion in negative:
                    st.write('该视频情绪是消极的')#显示语言
                else:
                    st.write('该视频情绪是中立的')#显示语言

                option = {'grid': {'top': 10, 'left': 50, 'right': 50, 'bottom': 50},
                        'tooltip': {'trigger': 'axis', 'confine': 'true'},
                        'yAxis': {'triggerEvent': 'true', 'data': emotion_key},
                        'xAxis': {},
                        'series': [{'name': 'emotion', 'type': 'bar', 'data': emotion_list,
                                    'itemStyle': {'normal': {
                                        'label': {
                                            'show': 'true',
                                            'position': 'right',
                                            'textStyle': {'color': 'black'}
                                        }
                                    }}}]
                        }
                st_echarts(options=option, height='500px', width='700px')

                # modality emotion
                data = pd.read_csv('result_modality.csv', encoding='utf-8', sep=';')
                option = {  # 提示框，鼠标悬浮交互时的信息提示
                    'title': {'text': ' 单模态分析结果'},
                    'tooltip': {'show': 'true',  # 是否显示
                                'trigger': 'axis',  # 触发类型，默认数据触发，见下图，可选为：'item' | 'axis'
                                'axisPointer': {
                                    'type': 'shadow'
                                }
                                },
                    'legend': {},
                    'grid': {
                        'left': '3%',
                        'right': '4%',
                        'bottom': '3%',
                        'containLabel': 'true'
                    },
                    'xAxis': {
                        'type': 'value'
                    },
                    'yAxis': {
                        'type': 'category',
                        'data': [' 文本', '视频', '音频']
                    },
                    'series': [
                        {
                            'name': '生气',
                            'type': 'bar',
                            'stack': 'total',
                            'label': {
                                'show': 'true'
                            },
                            'emphasis': {
                                'focus': 'series'
                            },
                            'data': [float(data['angry'][i]) for i in range(3)]
                        },
                        {
                            'name': '反感',
                            'type': 'bar',
                            'stack': 'total',
                            'label': {
                                'show': 'true'
                            },
                            'emphasis': {
                                'focus': 'series'
                            },
                            'data': [float(data['disgusted'][i]) for i in range(3)]
                        },
                        {
                            'name': '害怕',
                            'type': 'bar',
                            'stack': 'total',
                            'label': {
                                'show': 'true'
                            },
                            'emphasis': {
                                'focus': 'series'
                            },
                            'data': [float(data['fear'][i]) for i in range(3)]
                        },
                        {
                            'name': '高兴',
                            'type': 'bar',
                            'stack': 'total',
                            'label': {
                                'show': 'true'
                            },
                            'emphasis': {
                                'focus': 'series'
                            },
                            'data': [float(data['happy'][i]) for i in range(3)]
                        },
                        {
                            'name': '悲伤',
                            'type': 'bar',
                            'stack': 'total',
                            'label': {
                                'show': 'true'
                            },
                            'emphasis': {
                                'focus': 'series'
                            },
                            'data': [float(data['sad'][i]) for i in range(3)]
                        },
                        {
                            'name': '惊讶',
                            'type': 'bar',
                            'stack': 'total',
                            'label': {
                                'show': 'true'
                            },
                            'emphasis': {
                                'focus': 'series'
                            },
                            'data': [float(data['surprise'][i]) for i in range(3)]
                        }

                    ]
                }
                st_echarts(options=option, height='500px')

        #视频分句情感波动图
                clips_num=0
                emotion_clip_list=[]
                with open('result_clip_1.txt','r') as f:
                    for line in f.readlines():
                        line=line.strip()
                        line=line.split('\t')
                        line=list(map(float,line))
                        emotion_clip_list.append(line)
                for i in range(len(emotion_clip_list)):
                    emotion_clip_list[i]=np.argmax(emotion_clip_list[i])
                print(emotion_clip_list)
                option={'title':{'text':'视频情感波动图'},
                        'xAxis':{'type':'category','data':[f'{i}_分片' for i in range(len(emotion_clip_list))]},
                        'yAxis':{'name':'情感分类','type': 'value' , 'data':[i for i in range(len(emotion_key))]},
                        'tooltip':{'show':'true',
                                    'trigger':'axis'},
                        'series':[{'name':'视频情感波动曲线','type':'line','data':[int(i) for i in emotion_clip_list]}]
                        }
                st_echarts(options=option,height='500px')
                st.write('情感类型： 0--生气 1--反感 2--害怕 3--高兴 4--悲伤 5--惊讶')





if side_bar=='English':


    choice = st.selectbox('analysis', ['video_emotion_analysis'])

    
    if choice == 'video_emotion_analysis':
        uploaded_file = st.file_uploader('upload your file here')
        if uploaded_file is not None:
            st.success('upload success')
            fn = uploaded_file.name.split('.')[0]
            mp4_path = f'mp4/{fn}.mp4'
            st.video(mp4_path)

        btn_ea = st.button('emotion analysis')

        if btn_ea:
            fn = uploaded_file.name.split('.')[0]
            V2EM_prediction.main_for_st.emotion_analysis(str(fn))

            # general emotion
            emotion_list = []
            with open('result.txt', 'r') as f:
                for line in f.readlines():
                    line = line.strip('\n')
                    emotion_list.append(line)
            print(emotion_list)

            emotion_key = ['angry', 'excited', 'frustrated', 'happy', 'neutral', 'sad']#iemocap
           ##emotion_key = ['angry', 'disgusted', 'fear', 'happy', 'sad', 'surprise']  # mosei
            max_emotion = emotion_key[np.argmax(emotion_list)]
            positive = ['happy', 'surprise','excited','neutral']
            negative = ['angry', 'disgusted', 'fear', 'sad','frustrated']
            if max_emotion in positive:
                st.write('video emotion is positive')
            if max_emotion in negative:
                st.write('video emotion is negative')
            option = {'grid': {'top': 10, 'left': 50, 'right': 50, 'bottom': 50},
                      'tooltip': {'trigger': 'axis', 'confine': 'true'},
                      'yAxis': {'triggerEvent': 'true', 'data': emotion_key},
                      'xAxis': {},
                      'series': [{'name': 'emotion', 'type': 'bar', 'data': emotion_list,
                                  'itemStyle': {'normal': {
                                      'label': {
                                          'show': 'true',
                                          'position': 'right',
                                          'textStyle': {'color': 'black'}
                                      }
                                  }}}]
                      }
            st_echarts(options=option, height='500px', width='700px')

            # clip emotion tendency
            emotion_clip_list = []
            with open('result_clip.txt', 'r') as f:
                for line in f.readlines():
                    line = line.strip()
                    line = line.split('\t')
                    line = list(map(float, line))
                    emotion_clip_list.append(line)

            for i in range(len(emotion_clip_list)):
                emotion_clip_list[i] = np.argmax(emotion_clip_list[i])

            print(emotion_clip_list)

            option = {'title': {'text': 'video emotion tendency'},
                      # 'xAxis': {'type': 'value', 'data': [i for i in range(len(emotion_clip_list))],
                      #           'axisLabel':{'formmatter':'{value}_clip'}},
                      'xAxis': {'type': 'category', 'data': [f'{i}_clip' for i in range(len(emotion_clip_list))]},
                      'yAxis': {'name': 'emotion kind', 'type': 'value', 'data': [i for i in range(len(emotion_key))]},
                      # 提示框，鼠标悬浮交互时的信息提示
                      'tooltip': {'show': 'true',  # 是否显示
                                  'trigger': 'axis',  # 触发类型，默认数据触发，见下图，可选为：'item' | 'axis'
                                  },
                      # 'dataZoom': {'type': 'slider', 'xAxisIndex': [0], 'show': 'true', 'height': 20, 'bottom': 0,
                      #              'zoomLock': 'true', 'minValueSpan': 0, 'maxValueSpan': 7, 'realtime': 'true',
                      #              'showDetail': 'false', 'filterMode': 'empty'},
                      'series':  # 折线图
                          [{'name': 'emotion_tendency', 'type': 'line', 'data': [int(i) for i in emotion_clip_list]}]
                      }
            st_echarts(options=option, height='500px')
            # st.write('emotion kind : 0--angry  1--disgusted   2--fear 3--happy  4--sad  5--surprise')#mosei
            st.write('emotion kind : 0--angry  1--excited   2--frustrated 3--happy  4--neutral  5--sad')#iemocap

            # modality emotion
            data = pd.read_csv('result_modality.csv', encoding='utf-8', sep=';')
            option = {  # 提示框，鼠标悬浮交互时的信息提示
                'title':{'text':'modality'},
                'tooltip': {'show': 'true',  # 是否显示
                            'trigger': 'axis',  # 触发类型，默认数据触发，见下图，可选为：'item' | 'axis'
                            'axisPointer': {
                                'type': 'shadow'
                            }
                            },
                'legend': {},
                'grid': {
                    'left': '3%',
                    'right': '4%',
                    'bottom': '3%',
                    'containLabel': 'true'
                },
                'xAxis': {
                    'type': 'value'
                },
                'yAxis': {
                    'type': 'category',
                    'data': ['text', 'visual', 'audio']
                },
                'series': [
                    {
                        'name': 'angry',
                        'type': 'bar',
                        'stack': 'total',
                        'label': {
                            'show': 'true'
                        },
                        'emphasis': {
                            'focus': 'series'
                        },
                        'data': [float(data['angry'][i]) for i in range(3)]
                    },
                    {
                        'name': 'excited',
                        'type': 'bar',
                        'stack': 'total',
                        'label': {
                            'show': 'true'
                        },
                        'emphasis': {
                            'focus': 'series'
                        },
                        'data': [float(data['disgusted'][i]) for i in range(3)]
                    },
                    {
                        'name': 'frustrated',
                        'type': 'bar',
                        'stack': 'total',
                        'label': {
                            'show': 'true'
                        },
                        'emphasis': {
                            'focus': 'series'
                        },
                        'data': [float(data['fear'][i]) for i in range(3)]
                    },
                    {
                        'name': 'happy',
                        'type': 'bar',
                        'stack': 'total',
                        'label': {
                            'show': 'true'
                        },
                        'emphasis': {
                            'focus': 'series'
                        },
                        'data': [float(data['happy'][i]) for i in range(3)]
                    },
                    {
                        'name': 'neutral',
                        'type': 'bar',
                        'stack': 'total',
                        'label': {
                            'show': 'true'
                        },
                        'emphasis': {
                            'focus': 'series'
                        },
                        'data': [float(data['sad'][i]) for i in range(3)]
                    },
                    {
                        'name': 'sad',
                        'type': 'bar',
                        'stack': 'total',
                        'label': {
                            'show': 'true'
                        },
                        'emphasis': {
                            'focus': 'series'
                        },
                        'data': [float(data['surprise'][i]) for i in range(3)]
                    }

                ]
            }
            st_echarts(options=option, height='500px')
          