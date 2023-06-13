import argparse
import json
import os

import emoji

if __name__ == "__main__":
    # paremeters
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--region",
        type=str,
        default="Hawaii",
        help="the region name of datasets(e.g. California)",
    )
    args, _ = parser.parse_known_args()

    # path设置
    parent_path = "./dataset/" + args.region + "/"
    if not os.path.exists(parent_path):
        os.mkdir(parent_path)
    dataset_path = parent_path + "review-" + args.region + "_10.json"
    pois_reviews_file_path = parent_path + "pois_reviews.json"

    # 字典，key为gmap_id（':'替换为'-'），value为text列表（review评论集合）
    review_dict = dict()

    # 打开review-xxx_10.json文件
    reivew10_file = open(dataset_path, "r")
    # 遍历meta-xxx.json，row_i为行号，line为一行数据
    for row_i, line in enumerate(reivew10_file):
        # 解析json对象，得到字典
        obj = json.loads(line)

        # 取出gmap_id和text
        gmap_id = obj["gmap_id"].replace(":", "-")
        text = obj["text"]

        text_list = review_dict.get(gmap_id)
        if text is not None:
            # text不为空
            # 对text处理，几种情况：1. 2. 3. 4.
            # 1.text被google翻译了
            if text.find('(Translated by Google)') != -1:
                list = text.split('(Original)') # 根据'(Original)'做分割，之前是英文，之后是原语言
                text = list[0] # 只保留英文
                text = text.replace('(Translated by Google)', '') # '(Translated by Google)'替换成空串
                text = text.replace('\n', '') # '\n'替换成空串。？句子中的回车怎么处理？
                text = text.lstrip() # 删除一个字符串开头的空格
            # 2.长度超过2048，截断
            if len(text) > 2048:
                text = text[:2048]
            # 3.emoji
            text = emoji.replace_emoji(text, replace='') # 将Unicode编码的表情替换为空串
            # 4.Unicode转换，可以不转换
            text = text.replace('\u2019', '\'')
            
        else:
            # text为空，防止对应gmap_id的text都为空，造成gmap_id的缺失，初始化一个空数组
            if text_list is None:
                review_dict[gmap_id] = []
            # 并且不继续执行，防止给数组中添加一个None
            continue
        
        # 保存到字典reivew_dict中
        if text_list is None:
            text_list = [text]
            review_dict[gmap_id] = text_list
        else:
            text_list.append(text)

        # 打印处理进度
        if row_i % 10000 == 0:
            print(f'get_review===已处理:{row_i+1}===已有poi数量:{len(review_dict)}')

    # 打开poi_review.json文件
    pois_reviews_file = open(pois_reviews_file_path, "w")
    # 保存转换结果
    for key, value in review_dict.items():
        pois_reviews_file.write(json.dumps({key: value}) + '\n' )
    
    reivew10_file.close()
    pois_reviews_file.flush()
    pois_reviews_file.close()
