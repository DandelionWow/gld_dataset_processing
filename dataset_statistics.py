# Author: S_Sun(create)

import json
from datetime import datetime
import time
import pickle
import os


def handle_dataset_review(file_path, review_file_name):
    with open(file_path+review_file_name, 'r') as review_file:
        user_id_set = set()
        user_dict = dict()
        time_list = list()
        time_set = set()
        misc_info_category_set = set()

        for index, line in enumerate(review_file):
            json_obj = json.loads(line)

            user_id_set.add(json_obj['user_id'])

            if user_dict.get(json_obj['user_id']) == None:
                user_dict[json_obj['user_id']] = [{'time':json_obj['time'], 'text':json_obj['text'], 'pics':json_obj['pics'], 'gmap_id':json_obj['gmap_id']}]
            else:
                user_dict[json_obj['user_id']].append({'time':json_obj['time'], 'text':json_obj['text'], 'pics':json_obj['pics'], 'gmap_id':json_obj['gmap_id']})
            
            time_list.append(json_obj['time'])
            time_set.add(json_obj['time'])

            misc_info = json_obj['MISC']
            misc_info_category_set.add(misc_info.keys())
        
        # 保存几个集合
        with open(file_path+'user_id_set.pkl', 'wb') as f:
            pickle.dump(user_id_set, f)
        with open(file_path+'user_dict.pkl', 'wb') as f:
            pickle.dump(user_dict, f)
        with open(file_path+'time_list.pkl', 'wb') as f:
            pickle.dump(time_list, f)
        with open(file_path+'time_set.pkl', 'wb') as f:
            pickle.dump(time_set, f)
        with open(file_path+'misc_info_category_set.pkl', 'wb') as f:
            pickle.dump(misc_info_category_set, f)

        return user_id_set, user_dict, time_list, time_set

def statistics_4_review_10(file_path, file_name):
    if (
        os.path.exists(file_path+'user_id_set.pkl') 
        and os.path.exists(file_path+'user_dict.pkl') 
        and os.path.exists(file_path+'time_list.pkl')
        and os.path.exists(file_path+'time_set.pkl')
        ):
        # 加载处理后的数据
        with open(file_path+'user_id_set.pkl', 'rb') as f:
            user_id_set = pickle.load(f)
        with open(file_path+'user_dict.pkl', 'rb') as f:
            user_dict = pickle.load(f)
        with open(file_path+'time_list.pkl', 'rb') as f:
            time_list = pickle.load(f)
        with open(file_path+'time_set.pkl', 'rb') as f:
            time_set = pickle.load(f)
    else:
        # 处理数据集
        user_id_set, user_dict, time_list, time_set = handle_dataset_review(file_path, file_name)
    
    
    # 打印统计信息
    # user_id数量
    print(f"用户数量==={len(user_id_set)}") 
    # 最早时间和最晚时间
    min_time = min(time_set, key=lambda time: time)
    max_time = max(time_set, key=lambda time: time)
    print(f"最早时间==={datetime.fromtimestamp(int(min_time/1000)).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"最晚时间==={time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(max_time/1000)))}")
    min_year = datetime.fromtimestamp(int(min_time/1000)).year
    max_year = datetime.fromtimestamp(int(max_time/1000)).year
    # 每个年份数量统计
    year_couts = {}
    for index, timestamp in enumerate(time_list):
        year = datetime.fromtimestamp(int(timestamp/1000)).year
        if year >= min_year and year <= max_year:
            if year not in year_couts:
                year_couts[year] = 1
            else:
                year_couts[year] += 1
    print(f"每个年份数量统计==={year_couts}")

def handle_dataset_meta(file_path, file_name):
    with open(file_path+file_name, 'r') as f:
        misc_info_category_set = set()

        for index, line in enumerate(f):
            json_obj = json.loads(line)

            misc_info = json_obj['MISC']
            if misc_info is not None:
                misc_info_category_set.update(misc_info.keys())
        
        # 保存几个集合
        with open(file_path+'misc_info_category_set.pkl', 'wb') as f:
            pickle.dump(misc_info_category_set, f)

        return misc_info_category_set

def statistics_4_meta(file_path, file_name):
    if (
        os.path.exists(file_path+'misc_info_category_set.pkl') 
        ):
        # 加载处理后的数据
        with open(file_path+'misc_info_category_set.pkl', 'rb') as f:
            misc_info_category_set = pickle.load(f)
            # 合并set集，追加更新（先不用）
            # misc_info_category_set_ = handle_dataset_meta(file_path, file_name)
            # misc_info_category_set = misc_info_category_set | misc_info_category_set_
            # pickle.dump(misc_info_category_set, f)
            
    else:
        # 处理数据集
        misc_info_category_set = handle_dataset_meta(file_path, file_name)
    
    # 打印
    print(len(misc_info_category_set))

if __name__=='__main__':
    region = 'California'
    file_path = './dataset/' + region + '/'
    review_10_file_name = 'review-' + region + '_10.json'
    meta_file_name = 'meta-' + region + '.json'

    # statistics_4_review_10(file_path, review_10_file_name)
    statistics_4_meta(file_path, meta_file_name)

    # misc_info_category_set = set()
    # misc_info_category_set_ = set()
    # with open(file_path+'misc_info_category_set.pkl', 'rb') as f:
    #     misc_info_category_set = pickle.load(f)