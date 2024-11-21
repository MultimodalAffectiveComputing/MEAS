import torch
from tqdm import tqdm
from src.trainers.basetrainer import TrainerBase
from transformers import AlbertTokenizer,RobertaTokenizer
import numpy as np
import csv

class IemocapTrainer(TrainerBase):
    def __init__(self, args, model, criterion, optimizer, scheduler, device, dataloaders):
        super(IemocapTrainer, self).__init__(args, model, criterion, optimizer, scheduler, device, dataloaders)

        self.args = args
        self.text_max_len = args['text_max_len']
        self.tokenizer =RobertaTokenizer.from_pretrained('pretrained/roberta-base')
        #self.tokenizer = AlbertTokenizer.from_pretrained('./src/models/albert-base-v2')
        self.all_test_stats = []
        annotations = dataloaders['test'].dataset.get_annotations()
        self.best_epoch = -1

    def test(self):
        test_stats = self.eval_one_epoch('test')
        return test_stats

    def eval_one_epoch(self, phase='valid', thresholds=None):

        for m in self.model.modules():
            if hasattr(m, 'switch_to_deploy'):
                m.switch_to_deploy()  # turn to deploy every modules
        self.model.eval()
        dataloader = self.dataloaders[phase]

        data_size = 0
        total_logits = []
        video_logits=[]
        audio_logits=[]
        text_logits=[]
        total_Y = []
        pbar = tqdm(dataloader, desc=phase)

        for uttranceId, imgs, imgLens, specgrams, specgramLens, text in pbar:
            text = self.tokenizer(text, return_tensors='pt', max_length=self.text_max_len, padding='max_length', truncation=True)

            # imgs = imgs.to(device=self.device)
            specgrams = specgrams.to(device=self.device)
            text = text.to(device=self.device)

            with torch.set_grad_enabled(False):
                logits,text_logit,video_logit,audio_logit = self.model(imgs, imgLens, specgrams, specgramLens, text) # (batch_size, num_classes)


            total_logits.append(logits.cpu())
            video_logits.append(video_logit.cpu())
            audio_logits.append(audio_logit.cpu())
            text_logits.append(text_logit.cpu())

        #test_zyq!!!
        total_logits = torch.cat(total_logits, dim=0)
        total_video_logits = torch.cat(video_logits, dim=0)
        total_video_logits=torch.where(torch.isnan(total_video_logits), torch.full_like(total_video_logits, 0), total_video_logits)
        total_text_logits = torch.cat(text_logits, dim=0)
        total_audio_logits = torch.cat(audio_logits, dim=0)
        mean_video_logits = torch.mean(total_video_logits, dim=0)
        mean_video_preds = torch.sigmoid(mean_video_logits)
        mean_audio_logits = torch.mean(total_audio_logits, dim=0)
        mean_audio_preds = torch.sigmoid(mean_audio_logits)
        mean_text_logits = torch.mean(total_text_logits, dim=0)
        mean_text_preds = torch.sigmoid(mean_text_logits)
        print(mean_text_preds)

        with open("result_modality.csv",'w+', errors='ignore', newline='', encoding='utf-8') as f:
            writer1 = csv.writer(f, delimiter=';')
            writer1.writerow(['angry','disgusted','fear','happy','sad','surprise'])
            writer1.writerow(logit for logit in np.array(mean_text_preds) )
            writer1.writerow(logit for logit in np.array(mean_video_preds) )
            writer1.writerow(logit for logit in np.array(mean_audio_preds) )
        print("write txt_modality finish!")## save result_clip.txt

        with open("result_clip_1.txt", 'w+') as f:
            logit_clips = np.array(total_logits)
            for i in range(len(logit_clips)):
                for j in range(len(logit_clips[i])):
                    f.write(str(logit_clips[i][j]))
                    f.write('\t')
                f.write('\n')
        print("write txt_clips finish!")## save result_clip.txt

        total_logits=torch.where(torch.isnan(total_logits), torch.full_like(total_logits, 0), total_logits)
        mean_logits = torch.mean(total_logits, dim=0)
        mean_preds = torch.sigmoid(mean_logits)
        # print(total_logits)
        # print('six emotional values for one video:'+'\n')
        print(mean_preds)



        # with open("result.txt", 'a') as f:
        #     f.write(f'{uttranceId[0]},{np.argmax(mean_preds.numpy())}')
        #     f.write('\n')
        # print("write txt finish!")## save result.txt

        with open("result_clip.txt", 'w+') as f:
            logit_clips = np.array(total_logits)
            for i in range(len(logit_clips)):
                for j in range(len(logit_clips[i])):
                    f.write(str(logit_clips[i][j]))
                    f.write('\t')
                f.write('\n')
        print("write txt_clips finish!")## save result_clip.txt


        return mean_preds
