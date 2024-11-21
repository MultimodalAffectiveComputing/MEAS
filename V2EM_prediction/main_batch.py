#for batch videos and audios
#replace basepath
import os
import time
import torch
import numpy as np
from torch.utils.data import DataLoader
from src.cli import get_args
# from src.datasets import get_dataset_iemocap, collate_fn
# from src.trainers.r_emotiontrainer import IemocapTrainer
from src.models.c_e2e import MME2E

from src.datasets_news_test_batch  import get_dataset_iemocap, collate_fn
from src.trainers.r_emotiontrainer_news_test import IemocapTrainer

import csv
import sys
import os

def get_mp4_filenames(directory):
    files = os.listdir(directory)
    mp4_files = [str(file.replace('.mp4','')) for file in files if file.endswith('.mp4')]
    return mp4_files

def emotion_analysis(id,basepath):
    start = time.time()

    sys.argv = ['main.py', '-lr=4.5e-6', '-ep=40', '-mod=tav', '-bs=1', '--img-interval=500', '--early-stop=6',
                '--loss=bce', '--cuda=0', '--model=mme2e', '--num-emotions=2', '--trans-dim=64', '--trans-nlayers=4',
                '--trans-nheads=4', '--text-lr-factor=10', '--text-model-size=base', '--text-max-len=100', '--test',
                '--datapath=../IEMOCAP_PREPROCESS_10']

    args = get_args()

    # Fix seed for reproducibility
    seed = args['seed']
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # Set device
    os.environ["CUDA_VISIBLE_DEVICES"] = args['cuda']
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    # input data
    test_dataset = get_dataset_iemocap(id=id,base_path=basepath,data_folder=args['datapath'], phase='test',
                                       img_interval=args['img_interval'], hand_crafted_features=args['hand_crafted'])
    test_loader = DataLoader(test_dataset, batch_size=args['batch_size'], shuffle=False,
                             num_workers=0, collate_fn=collate_fn)


    dataloaders = {
        'test': test_loader
    }

    lr = args['learning_rate']
    if args['model'] == 'mme2e':
        model = MME2E(args=args, device=device)
        model = model.to(device=device)

        # When using a pre-trained text modal, you can use text_lr_factor to give a smaller leraning rate to the textual model parts
        if args['text_lr_factor'] == 1:
            optimizer = torch.optim.Adam(model.parameters(), lr=args['learning_rate'],
                                         weight_decay=args['weight_decay'])
        else:
            optimizer = torch.optim.Adam([
                {'params': model.T.parameters(), 'lr': lr / args['text_lr_factor']},
                {'params': model.t_out.parameters(), 'lr': lr / args['text_lr_factor']},
                {'params': model.V.parameters()},
                {'params': model.v_flatten.parameters()},
                {'params': model.v_transformer.parameters()},
                {'params': model.v_out.parameters()},
                {'params': model.A.parameters()},
                {'params': model.a_flatten.parameters()},
                {'params': model.a_transformer.parameters()},
                {'params': model.a_out.parameters()},
                {'params': model.weighted_fusion.parameters()},
            ], lr=lr, weight_decay=args['weight_decay'])
    checkpoint = torch.load(
        '/home/system/mseva/MSEVA-System/news_analysis_system_zyq/V2EM_prediction/savings/models/mme2e_tav_mosei_roberta-base_Acc_0.8660_F1_0.8663_AUC_0.9013_imginvl800_seed0.pt',
        #"savings/models/mme2e_tav_Acc_0.7134_F1_0.4681_AUC_0.7356_imginvl500_seed0.pt",#mosei
        #"savings/models/mme2e_tav_Acc_0.8477_F1_0.5857_AUC_0.8747_imginvl500_seed0.pt",#iemocap
        map_location='cuda:0')  # pycharm run
    # checkpoint = torch.load("./savings/models/mme2e_tav_Acc_0.8477_F1_0.5857_AUC_0.8747_imginvl500_seed0.pt", map_location='cuda:0')#pycharm run
    model.load_state_dict(checkpoint,
                          False)  # load best model(when valid and test add,while when train must //this sentence)

    scheduler = None
    criterion = None

    trainer = IemocapTrainer(args, model, criterion, optimizer, scheduler, device, dataloaders)

    total_logits=trainer.test()

    end = time.time()

    print(f'Total time usage = {(end - start) :.2f} seconds.')

    return  total_logits


if __name__ == "__main__":
    st=time.time()
    #basepath = '/media/ExtHDD02/zyq/news_dataset2'
    basepath = '/home/datasets/bilinews_1_preprocessed'
    directory='/home/datasets/dataset_marked_1/video'
    ids=get_mp4_filenames(directory)

    #id=input('id:')
    for id in ids:
        logits = emotion_analysis(int(id), basepath).numpy()
        #emo_dict = {0: 'angry', 1: 'disgusted', 2: 'fear', 3: 'happy', 4: 'sad', 5: 'surprise'}#mosei
        #emo_dict={0:'angry',1:"excited", 2:"frustrated",3:"happy", 4:"neutral", 5:"sad"}
        #emotion = emo_dict[np.argmax(logits)]
        print(id, np.argmax(logits))
        with open("result.txt", 'a') as f:
            f.write(f'{id},{np.argmax(logits)}')
            f.write('\n')
        print("write txt finish!")## save result.txt

        # pid=list(set(os.popen('fuser -v /dev/nvidia*').read().split()))
        # kill_cmd='kill -9 '+' '.join(pid)
        # print(kill_cmd)
        # os.popen(kill_cmd)
    et=time.time()
    cost_t=et-st
    print('cost:',cost_t)


