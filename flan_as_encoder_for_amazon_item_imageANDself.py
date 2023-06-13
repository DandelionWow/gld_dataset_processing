# Author: T_Xu(create), S_Sun(modify)

import argparse
import json
import numpy as np
from transformers import pipeline
import torch
import time
import pandas as pd

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class CustomPipeline:
    def __init__(self, model_name, gpu_index):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, device_map={"": 'cuda:'+str(gpu_index)})
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, device_map={"": 'cuda:'+str(gpu_index)})

    def get_embedding(self, input_text):
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt")
        decoder_input_ids = self.tokenizer.encode("", return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, decoder_input_ids=decoder_input_ids)
            hidden_states = outputs.encoder_last_hidden_state
        cls_embedding = hidden_states[:, 0, :]
        return cls_embedding


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

def embed_4_modal_meta(file_path, target_file_path):
    count = 1
    time_start = time.time()
    # 先读取一遍filename记录总行数
    total_num = 0
    with open(file_path, 'r') as f:
        for line in f:
            total_num += 1

    target_file = open(target_file_path, 'w')

    # 逐条读取filename
    with open(file_path, 'r') as f:
        for line in f:
            # 解析json
            line = json.loads(line)
            kv = line.popitem()
            poi_id = kv[0]
            des = kv[1]
        
            # embed
            cls_embedding = custom_pipeline.get_embedding(des)
            cls_embedding = cls_embedding.tolist()

            # 写入文件
            target_file.write(json.dumps({poi_id: cls_embedding}) + '\n')
        
            # 计算剩余时间
            time_end = time.time()
            time_left = (time_end - time_start) / (count + 1) * (total_num - count)
            # 将time_left按照时分秒格式输出
            time_left = time.strftime("%H:%M:%S", time.gmtime(time_left))
            print('count:', count, 'poi_id:', poi_id, 'time_left:', time_left)
            count += 1

    target_file.flush()
    target_file.close()

def embed_4_modal_image(file_path, target_file_path):
    # 用于计算时间
    count = 1
    time_start = time.time()
    # 先读取一遍filename记录总行数
    total_num = 0
    with open(file_path, 'r') as f:
        for line in f:
            total_num += 1

    # 打开目标写入文件
    target_file = open(target_file_path, 'w')

    # 逐条读取filename
    with open(file_path, 'r') as f:
        for line in f:
            # 解析json
            line = json.loads(line)
            kv = line.popitem()
            poi_id = kv[0]
            des_list = kv[1]

            embeddings = []
            for des in des_list: # 这里没有做空处理，因为image_des中没有空集合
                cls_embedding = custom_pipeline.get_embedding(des)
                cls_embedding = cls_embedding.tolist()
                embeddings.append(cls_embedding)
            # 求和成为一个embedding，形状跟单个cls_embedding一样
            summed_embedding = np.sum(embeddings, axis=0)
            # 归一化
            normalized_embedding = summed_embedding / np.linalg.norm(summed_embedding)
            normalized_embedding = normalized_embedding.tolist()
            # 写入文件
            target_file.write(json.dumps({poi_id: normalized_embedding}) + '\n')
            # 计算剩余时间
            time_end = time.time()
            time_left = (time_end - time_start) / (count + 1) * (total_num - count)
            # 将time_left按照时分秒格式输出
            time_left = time.strftime("%H:%M:%S", time.gmtime(time_left))
            print('count:', count, 'poi_id:', poi_id, 'time_left:', time_left)
            count += 1
            
    target_file.flush()
    target_file.close()

def embed_4_modal_review_summary(file_path, target_file_path):
    # 用于计算时间
    count = 1
    time_start = time.time()
    # 先读取一遍filename记录总行数
    total_num = 0
    with open(file_path, 'r') as f:
        for line in f:
            total_num += 1

    # 打开目标写入文件
    target_file = open(target_file_path, 'w')

    # 逐条读取filename
    with open(file_path, 'r') as f:
        for line in f:
            # 解析json
            line = json.loads(line)
            kv = line.popitem() # [key, value]
            poi_id = kv[0] # key
            review_summary_list = kv[1] # value
            
            review_summary_embedding = None
            # 判断list是否为空
            if review_summary_list == []:
                # list为空，处理与pois_des一致，对空字符串做嵌入
                cls_embedding = custom_pipeline.get_embedding("")
                review_summary_embedding = cls_embedding.tolist()
            else:
                embeddings = []
                for review in review_summary_list:
                    cls_embedding = custom_pipeline.get_embedding(review)
                    cls_embedding = cls_embedding.tolist()
                    embeddings.append(cls_embedding)
                # 求和成为一个embedding，形状跟单个cls_embedding一样
                summed_embedding = np.sum(embeddings, axis=0)
                # 归一化
                normalized_embedding = summed_embedding / np.linalg.norm(summed_embedding)
                review_summary_embedding = normalized_embedding.tolist()
            # 写入文件
            target_file.write(json.dumps({poi_id: review_summary_embedding}) + '\n')
            # 计算剩余时间
            time_end = time.time()
            time_left = (time_end - time_start) / (count + 1) * (total_num - count)
            # 将time_left按照时分秒格式输出
            time_left = time.strftime("%H:%M:%S", time.gmtime(time_left))
            print('count:', count, 'poi_id:', poi_id, 'time_left:', time_left)
            count += 1
            
    target_file.flush()
    target_file.close()

if __name__ == '__main__':
    # paremeters
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', type=str, default='Hawaii', help='the region name of datasets(e.g. California)')
    parser.add_argument('--gpu_index', type=str, default='3', help='the index of cuda')
    args, _ = parser.parse_known_args()

    parent_path = './dataset/' + args.region + '/'

    model_name = "declare-lab/flan-alpaca-xl"
    custom_pipeline = CustomPipeline(model_name, args.gpu_index)
    
    # 处理pois_description.json，对其做嵌入
    pois_description_file_path = parent_path + 'pois_description.json'
    modal_meta_embedding_file_path = parent_path + 'modal_meta_embedding.json'
    embed_4_modal_meta(pois_description_file_path, modal_meta_embedding_file_path)

    # 处理image_description.json，对其做嵌入
    image_description_file_path = parent_path + 'image_description.json'
    modal_image_embedding_file_path = parent_path + 'modal_image_embedding.json'
    embed_4_modal_image(image_description_file_path, modal_image_embedding_file_path)

    # 处理review_summary.json，对其做嵌入
    review_summary_file_path = parent_path + 'review_summary.json'
    modal_review_summary_embedding_file_path = parent_path + 'modal_review_summary_embedding.json'
    embed_4_modal_review_summary(review_summary_file_path, modal_review_summary_embedding_file_path)
