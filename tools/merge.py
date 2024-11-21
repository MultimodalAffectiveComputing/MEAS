##merge script_file for translation
import pandas as pd
import os

for i in range(50):
    id=i+51
    isExist = os.path.exists('/media/ExtHDD02/zyq/news_dataset2/script/{0}_script.csv'.format(id))
    csv_path='/media/ExtHDD02/zyq/news_dataset2/script/{0}_script.csv'.format(id)
    base='/media/ExtHDD02/zyq/news_dataset2'
    if isExist:
        translation=''
        data=pd.read_csv(csv_path,delimiter=';')
        texts=data['text'].values
        for string in texts:
            translation=translation+string

        with open(f'{base}/translation/{id}_translation.txt', 'w+', errors='ignore', encoding='utf-8') as f1:
            f1.writelines(translation)