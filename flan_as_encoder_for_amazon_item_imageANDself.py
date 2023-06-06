# Author: T_Xu(create), S_Sun(modify)

import json
from transformers import pipeline
import torch
import time
import pandas as pd

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class CustomPipeline:
    def __init__(self, model_name):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, device_map={"": 'cuda:3'})
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, device_map={"": 'cuda:3'})

    def get_embedding(self, input_text):
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt")
        decoder_input_ids = self.tokenizer.encode("", return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, decoder_input_ids=decoder_input_ids)
            hidden_states = outputs.encoder_last_hidden_state
        cls_embedding = hidden_states[:, 0, :]
        return cls_embedding

model_name = "declare-lab/flan-alpaca-xl"
custom_pipeline = CustomPipeline(model_name)


def run(filename, write_filename_image, write_filename_description):

    count = 1
    skip = 0
    time_start = time.time()
    # 先读取一遍filename记录总行数
    total_num = 0
    with open(filename, 'r') as f:
        for line in f:
            total_num += 1

    # 逐条读取filename
    with open(filename, 'r') as f:
        for line in f:
            if count <= skip:
                count += 1
                continue
            line = json.loads(line)
            asin = line['asin']
            category = line['category']
            description = line['description']
            # 如果description列表中的元素有包含html标签的，就去掉
            description = [i for i in description if '<' not in i]
            imageDescription = line['imageDescription']
            prompt_category = ''
            if category != []:
                prompt_category = 'My category : ' + ', '.join(category)
            prompt_description = ''
            if description != []:
                prompt_description = 'My description : ' + ' '.join(description)
            prompt_imageDescription = ''
            if imageDescription != []:
                prompt_imageDescription = 'My image description : ' + '; '.join(imageDescription)

            if imageDescription != []:
                prompt = prompt_imageDescription
                text_len = len(prompt)
                if text_len > 2048:
                    text_list = prompt.split(' ')
                    text_list_ = []
                    for i in range(0, text_len, 2048):
                        text_list_.append(' '.join(text_list[i:i + 2048]))
                    # 将text_list_中的每一份text进行embedding，然后相加取平均
                    cls_embedding = torch.zeros(1, 2048)
                    for text_ in text_list_:
                        cls_embedding += custom_pipeline.get_embedding(text_)
                    cls_embedding = cls_embedding / len(text_list_)
                    cls_embedding = cls_embedding.tolist()
                else:
                    cls_embedding = custom_pipeline.get_embedding(prompt)
                    cls_embedding = cls_embedding.tolist()

                # cls_embedding = custom_pipeline.get_embedding(prompt)
                # cls_embedding_ = cls_embedding.tolist()
                with open(write_filename_image, 'a') as f2:
                    f2.write(json.dumps({asin: cls_embedding}) + '\n')

            if description != [] or category != []:
                prompt = prompt_category + prompt_description

                text_len = len(prompt)
                if text_len > 2048:
                    text_list = prompt.split(' ')
                    text_list_ = []
                    for i in range(0, text_len, 2048):
                        text_list_.append(' '.join(text_list[i:i + 2048]))
                    # 将text_list_中的每一份text进行embedding，然后相加取平均
                    cls_embedding = torch.zeros(1, 2048)
                    for text_ in text_list_:
                        cls_embedding += custom_pipeline.get_embedding(text_)
                    cls_embedding = cls_embedding / len(text_list_)
                    cls_embedding = cls_embedding.tolist()
                else:
                    cls_embedding = custom_pipeline.get_embedding(prompt)
                    cls_embedding = cls_embedding.tolist()

                # cls_embedding = custom_pipeline.get_embedding(prompt)
                # cls_embedding_ = cls_embedding.tolist()
                with open(write_filename_description, 'a') as f3:
                    f3.write(json.dumps({asin: cls_embedding}) + '\n')

            if imageDescription == []:
                with open(write_filename_image, 'a') as f2:
                    f2.write(json.dumps({asin: cls_embedding}) + '\n')

            time_end = time.time()
            time_left = (time_end - time_start) / (count - skip + 1) * (total_num - count)
            # 将time_left按照时分秒格式输出
            time_left = time.strftime("%H:%M:%S", time.gmtime(time_left))
            print('count:', count, 'asin:', asin, 'time_left:', time_left)

            count += 1

# Musical   Video_Games   Cell_Phones_and_Accessories
filename = 'amazon/meta_Cell_Phones_and_Accessories_5core_with_imageDescription.json'
write_filename_image = 'amazon/Amazon_Cell_Phones_and_Accessories_image_embedding.json'
write_filename_description = 'amazon/Amazon_Cell_Phones_and_Accessories_description_embedding.json'
run(filename, write_filename_image, write_filename_description)

filename = 'amazon/meta_Musical_5core_with_imageDescription.json'
write_filename_image = 'amazon/Amazon_Musical_image_embedding.json'
write_filename_description = 'amazon/Amazon_Musical_description_embedding.json'
run(filename, write_filename_image, write_filename_description)

filename = 'amazon/meta_Video_Games_5core_with_imageDescription.json'
write_filename_image = 'amazon/Amazon_Video_Games_image_embedding.json'
write_filename_description = 'amazon/Amazon_Video_Games_description_embedding.json'
run(filename, write_filename_image, write_filename_description)