from transformers import AutoProcessor,AutoModelForSpeechSeq2Seq
import librosa
import whisper
import torch
import os
import csv
import time
from transformers import WhisperProcessor,WhisperForConditionalGeneration


from pydub import AudioSegment
from pydub.silence import split_on_silence,detect_silence

def translate(id):
    time_s=time.time()
    base='/media/ExtHDD02/zyq/news_dataset2'
    isExist=os.path.exists('audio_{0}/chunk0.wav'.format(id))
    if not isExist:
        os.mkdir('audio_{0}'.format(id))
        sound=AudioSegment.from_mp3(f'{base}/audio/{id}.wav')
        loundness=sound.dBFS
        print(loundness)

        se_list=detect_silence(sound,min_silence_len=900,silence_thresh=loundness-5)
        start=0
        l=len(se_list)
        for i,se in enumerate(se_list):
            middle=(se[0]+se[1])/2
            sound[start:middle].export('audio_{0}/chunk{1}.wav'.format(id,i),format="wav")
            start=middle
            if i==l-1:
                sound[start:len(sound)].export('audio_{0}/chunk{0}.wav'.format(id,i+1),format="wav")


    translation=''
    processor=WhisperProcessor.from_pretrained('/media/ExtHDD02/zyq/whisper-large-v2')
    model=WhisperForConditionalGeneration.from_pretrained('/media/ExtHDD02/zyq/whisper-large-v2')
    for i in range(50):
         path='audio_{0}/chunk{1}.wav'.format(id,i)
         if os.path.exists(path):
             speech_array, sampling_rate = librosa.load(path, sr=16000)
             inputs=processor(speech_array,sampling_rate=16000,return_tensors="pt").input_features
             forced_decoder_ids=processor.get_decoder_prompt_ids(language="zh",task="translate")
             predicted_ids=model.generate(inputs,forced_decoder_ids=forced_decoder_ids)
             transcription=processor.batch_decode(predicted_ids,skip_special_tokens=True)
             for i in range(len(transcription)):
                translation=translation+transcription[i]
    with open(f'{base}/translation/{id}_translation.txt', 'w+', errors='ignore', encoding='utf-8') as f1:
         f1.writelines(translation)

    # delete
    for root, dirs, files in os.walk('audio_{0}'.format(id), topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir('audio_{0}'.format(id))

    time_e=time.time()
    time_c=time_e-time_s
    print('cost time:',time_c)

if __name__ == '__main__':
    for i in range (50):
        id=i+1
        translate(id)
