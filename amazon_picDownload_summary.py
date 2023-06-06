# Author: T_Xu(create), S_Sun(modify)

import os
import urllib
import tqdm
import pandas as pd
import json
import time

# filter
meta_filename = 'amazon/meta_Video_Games.json'
filename = 'amazon/Video_Games_5.json'
write_filtered_filename = 'amazon/Video_Games_5core_filtered.json'


write_filename = 'amazon/mata_Video_Games_5core.json'
photo_dir = 'amazon/VG_photos/'

# 过滤meta数据集和review数据集
def filter():
    # 逐行读取filename，忽略有错误的行，将正确的行存入df中
    data = []
    with open(filename, 'r') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except:
                continue
    df = pd.json_normalize(data)

    # 取出df_meta中的asin
    asin_list = df['asin'].tolist()
    # 去重asin
    asin_set = set(asin_list)

    # 逐条读取meta_filename，将asin在asin_set中的行写入write_filename
    f = open(meta_filename, 'r')
    f_write = open(write_filename, 'w')
    for line in f:
        asin = json.loads(line)['asin']
        if asin in asin_set:
            f_write.write(line)
    f.close()
    f_write.close()

    # 取df中reviewerID, asin, overall, verified, reviewText, summary, reviewerName, unixReviewTime, reviewTime, style这些字段来构成新的df_write
    df_write = df[['reviewerID', 'asin', 'overall', 'verified', 'reviewText', 'summary', 'reviewerName', 'unixReviewTime', 'reviewTime']]
    # 将df_write中的每一行按照json格式写入write_filename

    f_write = open(write_filtered_filename, 'w')
    for i in range(len(df_write)):
        f_write.write(df_write.iloc[i].to_json() + '\n')
    f_write.close()

def download_image(skip_num=0):
    count = 1
    # 逐行读取write_filename，提取出asin和imageURLHighRes，将imageURLHighRes中的每张图片都下载到本地
    f = open(write_filename, 'r')
    for line in tqdm.tqdm(f):
        if count < skip_num:
            count += 1
            continue
        asin = json.loads(line)['asin']
        imageURLHighRes = json.loads(line)['imageURLHighRes']
        for i in range(len(imageURLHighRes)):
            url = imageURLHighRes[i]
            filename = photo_dir + asin + '_' + str(i) + '.jpg'
            # 重试 urllib.error.HTTPError: HTTP Error 404: Not Found
            try:
                urllib.request.urlretrieve(url, filename)
            except:
                try:
                    urllib.request.urlretrieve(url, filename)
                except:
                    try:
                        urllib.request.urlretrieve(url, filename)
                    except:
                        pass
    f.close()

def image_to_text(meta_filename, photo_dir_, write_filename_, cuda_no='cuda:0', skip_num=0):
    from PIL import Image
    from transformers import AutoProcessor, Blip2ForConditionalGeneration
    import torch
    processor = AutoProcessor.from_pretrained("Salesforce/blip2-opt-2.7b")
    model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b", torch_dtype=torch.float16)
    device = cuda_no if torch.cuda.is_available() else "cpu"
    model.to(device)

    prompt = ''

    # 将图像转换为文本，封装为一个函数
    def image2text(image_filename):
        image = Image.open(image_filename).convert('RGB')
        inputs = processor(image, text=prompt, return_tensors="pt").to(device, torch.float16)
        generated_ids = model.generate(**inputs, max_new_tokens=20)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
        return generated_text

    openfilename = meta_filename
    # 将photo_dir中的所有文件名存入filename_list
    filename_list = []
    for filename_ in os.listdir(photo_dir_):
        filename_list.append(filename_)

    count = 1
    null_num = 0
    time_start = time.time()
    # 打开文件openfilename，记录总行数
    f = open(openfilename, 'r')
    total_num = 0
    for line in f:
        total_num += 1
    f.close()

    # 逐行读取openfilename，提取出asin
    f = open(openfilename, 'r')
    for line in f:
        if count <= skip_num:
            count += 1
            continue
        # 将line转为字典
        line_dict = json.loads(line)
        asin = json.loads(line)['asin']
        # 在photo_dir所指向的目录中，找到以asin开头的文件，将其文件名存入filename_list
        asin_filename_list = []
        for filename_ in filename_list:
            if filename_.startswith(asin):
                asin_filename_list.append(filename_)
        # 删除字典中的similar_item, tech1
        del line_dict['tech1']
        del line_dict['similar_item']
        image_text_list = []
        for image_filename in asin_filename_list:
            image_text = image2text(photo_dir_ + image_filename)
            image_text_list.append(image_text)
        if image_text_list == []:
            null_num += 1
        # 将image_text_list添加到字典中
        line_dict['imageDescription'] = image_text_list
        # 将字典转为json格式，写入write_filename
        with open(write_filename_, 'a') as f_write:
            f_write.write(json.dumps(line_dict) + '\n')
        # 计算完成循环的剩余时间
        time_end = time.time()
        time_left = (time_end - time_start) / (count - skip_num + 1) * (total_num - count)
        # 转换为时分秒
        time_left = time.strftime("%H:%M:%S", time.gmtime(time_left))

        print(count, ' / ', total_num, ', time left: ', time_left, ' : ', image_text_list)
        count += 1
    f.close()
    print('null_num: ', null_num)


if __name__ == '__main__':
    # filter()
    # download_image(0)

    # 6  cell   15951   ---》  48210
    # 3  musical    ok  ---》  12200     null_num:  3323
    # 7  video  18260   ---》  21100

    image_to_text('amazon/mata_Cell_Phones_and_Accessories_5core.json',
     'amazon/CPA_photos/',
     'amazon/meta_Cell_Phones_and_Accessories_5core_with_imageDescription_part2.json',
     'cuda:1', skip_num=24000)