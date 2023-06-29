# Author: S_Peng(create), S_Sun(modify)

"""
过滤规则
1. 一个用户，在训练集和测试集上至少有一条轨迹，不满足条件的过滤掉。
2. NYC中POI和user的过滤阈值（交互的数量）是10。
3. NYC中轨迹划分按24小时，若某个轨迹只有一条交互，过滤掉。
4. NYC中，每条记录含有user，POI，POI Category，GPS，时间戳。
"""

import copy
import json
import datetime
import pytz
import pandas as pd
from datetime import datetime
import os
import pickle
import uuid

def filter_user_and_poi(file_path, pois_dict) -> dict:
    reviews_json_file = open(file_path, 'r', encoding="utf-8")

    # poi交互字典，key为poi_id，某POI有多少用户与之交互
    poi_user_dict = dict()
    for line in reviews_json_file:
        obj = json.loads(line)
        user_id = obj['user_id']
        poi_id = obj['gmap_id']

        if poi_user_dict.get(poi_id) is None:
            poi_user_dict[poi_id] = [user_id]
        else:
            poi_user_dict[poi_id].append(user_id)
    # 过滤掉小于10次交互的POI
    poi_user_dict_ = copy.deepcopy(poi_user_dict)
    for poi_id, user_list in poi_user_dict_.items():
        if len(user_list) < 10:
            poi_user_dict.pop(poi_id)
    poi_user_dict_.clear()
    
    # 用户交互字典，key为user_id，某个用户在什么时间什么位置与某POI交互
    user_poi_dict = dict()
    reviews_json_file.seek(0)
    for line in reviews_json_file:
        obj = json.loads(line)
        user_id = obj['user_id']
        poi_id = obj['gmap_id']
        timestamp = obj['time']

        # 跳过已过滤的poi
        if poi_user_dict.get(poi_id) is None:
            continue

        # key为时间戳，value为poi元信息（利用字典添加）
        pois = {
            timestamp: {
                'POI_id': poi_id,
                'POI_catid': pois_dict[poi_id]['POI_catid'],
                'POI_catid_code': pois_dict[poi_id]['POI_catid_code'],
                'POI_catname': pois_dict[poi_id]['POI_catname'],
                'latitude': pois_dict[poi_id]['latitude'],
                'longitude': pois_dict[poi_id]['longitude'],
            }
        }
        # 放入交互字典
        if user_poi_dict.get(user_id) is None:
            user_poi_dict[user_id] = pois
        else:
            user_poi_dict[user_id].update(pois)
    
    # 过滤掉小于10次交互的用户
    user_poi_dict_ = copy.deepcopy(user_poi_dict)
    for user_id, pois in user_poi_dict_.items():
        if len(pois) < 10:
            user_poi_dict.pop(user_id)
    user_poi_dict_.clear()

    return user_poi_dict

def split_filter_trajectory(user_poi_dict):
    user_trajectory_dict = dict()
    for user_id, pois in user_poi_dict.items():
        # 取出某user交互的所有poi，对time进行排序
        timestamp_list = list(pois.keys())
        timestamp_list.sort()
        # 初始化
        start_timestamp = timestamp_list[0]
        split_millisecond = 24*60*60*1000 # 分割时间
        trajectory_dict = {}
        trajectory_index = 1
        # 遍历timestamp_list
        for timestamp in timestamp_list:
            if timestamp - start_timestamp < split_millisecond:
                poi = pois.get(timestamp)
                trajectory_dict.update({
                    timestamp: poi
                })
            else:
                # 过滤掉trajectory中小于2的
                if len(trajectory_dict) < 2:
                    start_timestamp = timestamp
                    trajectory_dict = {}
                    poi = pois.get(timestamp)
                    trajectory_dict.update({
                        timestamp: poi
                    })
                    continue

                # 保存已分割的trajectory
                trajectory_id = user_id + '_' + str(trajectory_index)
                if user_trajectory_dict.get(user_id) is None:
                    user_trajectory_dict[user_id] = {trajectory_id: trajectory_dict}
                else:
                    user_trajectory_dict[user_id].update({trajectory_id: trajectory_dict})

                # 下一个trajectory，更新变量
                start_timestamp = timestamp
                trajectory_index += 1
                trajectory_dict = {}
                poi = pois.get(timestamp)
                trajectory_dict.update({
                    timestamp: poi
                })

    # 过滤掉只有一条轨迹的用户
    user_trajectory_dict_ = copy.deepcopy(user_trajectory_dict)
    for user_id, trajectory_dict in user_trajectory_dict_.items():
        if len(trajectory_dict) < 2:
            user_trajectory_dict.pop(user_id)
    user_trajectory_dict_.clear()

    return user_trajectory_dict

def get_pois_dict(file_path, poi_categroy_dict):
    meta_file = open(file_path, 'r')

    pois_dict = {}
    for line in meta_file:
        obj = json.loads(line)
        poi_id = obj['gmap_id']
        category = obj['category']
        latitude = obj['latitude']
        longitude = obj['longitude']

        POI_catid = None
        POI_catid_code = None
        if category is not None:
            POI_catid = poi_categroy_dict.get(category_list_2_str(category))['POI_catid']
            POI_catid_code = poi_categroy_dict.get(category_list_2_str(category))['POI_catid_code']
        
        pois_dict.update({
            poi_id: {
                'POI_catid': POI_catid,
                'POI_catid_code': POI_catid_code,
                'POI_catname': category,
                'latitude': latitude,
                'longitude': longitude,
            }
        })
    
    return pois_dict

def get_poi_categroy_dict(file_path):
    meta_file = open(file_path, 'r')

    category_dict = dict()
    catid_code = 1
    for line in meta_file:
        obj = json.loads(line)
        category_list = obj['category']

        if category_list is not None:
            category_str = category_list_2_str(category_list)
            if category_dict.get(category_str) is None:
                poi_category_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, category_str))
                poi_category_id = poi_category_id.replace('-', '')
                category_dict[category_str] = {'POI_catid': poi_category_id, 'POI_catid_code': catid_code}
                catid_code += 1

    return category_dict

def get_train_test_list(user_trajectory_dict):
    train_list = []
    test_list = []
    # 差timezone, norm_in_day_time
    for user_id, trajectory_dict, in user_trajectory_dict.items():
        trajectory_dict_len = len(trajectory_dict)
        for trajectory_id, user_poi_dict in trajectory_dict.items():
            trajectory_index = int(trajectory_id.split('_')[1])
            for timestamp, poi_dict in user_poi_dict.items():
                json_obj = dict()
                json_obj['user_id'] = user_id
                json_obj['POI_id'] = poi_dict['POI_id']
                json_obj['POI_catid'] = poi_dict['POI_catid']
                json_obj['POI_catid_code'] = poi_dict['POI_catid_code']
                json_obj['POI_catname'] = poi_dict['POI_catname']
                json_obj['latitude'] = poi_dict['latitude']
                json_obj['longitude'] = poi_dict['longitude']
                json_obj['UTC_time'] = get_utctime(timestamp)
                json_obj['local_time'] = get_localtime(timestamp, region)
                json_obj['day_of_week'] = get_day_of_week(timestamp, region)
                json_obj['trajectory_id'] = trajectory_id

                if trajectory_index < trajectory_dict_len * 0.8:
                    train_list.append(json_obj)
                    # train_list.append(json.dumps(json_obj))
                else:
                    test_list.append(json_obj)
                    # test_list.append(json.dumps(json_obj))

    return train_list, test_list

def category_list_2_str(list):
    if list is None:
        return ''
    
    category_str = ''
    for s in list:
        category_str += s + ','
    return category_str

# 时间相关方法
region_timezone_dict = {
    'Hawaii': 'US/Hawaii',
    'Alaska': 'US/Alaska'
}
def get_localtime(timestamp, region_name):
    tz = pytz.timezone(region_timezone_dict[region_name])
    dt = datetime.fromtimestamp(timestamp / 1000, tz)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt
def get_utctime(timestamp):
    utc_dt = datetime.fromtimestamp(timestamp / 1000, pytz.utc)
    utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
    return utc_dt
def get_day_of_week(timestamp, region_name):
    tz = pytz.timezone(region_timezone_dict[region_name])
    dt = datetime.fromtimestamp(timestamp / 1000, tz)
    return dt.weekday()

if __name__ == '__main__':
    dataset_dir = 'dataset'
    region = 'Hawaii'
    region_dir = os.path.join(os.curdir, dataset_dir, region)
    review_file_name = 'review-'+region+'_10.json'
    review_file_path = os.path.join(region_dir, review_file_name)
    meta_file_name = 'meta-'+region+'.json'
    meta_file_path = os.path.join(region_dir, meta_file_name)
    temp_pois_dict_file_path = os.path.join(region_dir, 'temp_pois_dict.pkl')
    temp_filtered_user_poi_file_path = os.path.join(region_dir, 'temp_filtered_user_poi_dict.pkl')
    temp_split_filtered_trajectory_file_path = os.path.join(region_dir, 'temp_user_trajectory_dict.pkl')
    temp_train_list_file_path = os.path.join(region_dir, 'temp_train_list.pkl')
    temp_test_list_file_path = os.path.join(region_dir, 'temp_test_list.pkl')

    # 生成POI Category字典，key为category_name_str，value为{POI_catid, POI_catid_code}
    poi_categroy_dict = get_poi_categroy_dict(meta_file_path)

    # 生成POI元信息（POI Category、latitude、longitude）(字典类型key为POI_id)
    pois_dict = {}
    if os.path.exists(temp_pois_dict_file_path):
        with open(temp_pois_dict_file_path, 'rb') as f:
            pois_dict = pickle.load(f)
    else:
        pois_dict = get_pois_dict(meta_file_path, poi_categroy_dict)
        with open(temp_pois_dict_file_path, 'wb') as f:
            pickle.dump(pois_dict, f)
    
    # 获取用户交互字典（已过滤小于10条的user和poi）
    user_poi_dict = {}
    if os.path.exists(temp_filtered_user_poi_file_path):
        with open(temp_filtered_user_poi_file_path, 'rb') as f:
            user_poi_dict = pickle.load(f)
    else:
        user_poi_dict = filter_user_and_poi(review_file_path, pois_dict)
        with open(temp_filtered_user_poi_file_path, 'wb') as f:
            pickle.dump(user_poi_dict, f)

    # 轨迹划分和过滤
    user_trajectory_dict = {}
    if os.path.exists(temp_split_filtered_trajectory_file_path):
        with open(temp_split_filtered_trajectory_file_path, 'rb') as f:
            user_trajectory_dict = pickle.load(f)
    else:
        user_trajectory_dict = split_filter_trajectory(user_poi_dict)
        with open(temp_split_filtered_trajectory_file_path, 'wb') as f:
            pickle.dump(user_trajectory_dict, f)
    
    # 获取train和test
    train_list = []
    test_list = []
    if os.path.exists(temp_train_list_file_path) and os.path.exists(temp_test_list_file_path):
        with open(temp_train_list_file_path, 'rb') as f:
            train_list = pickle.load(f)
        with open(temp_test_list_file_path, 'rb') as f:
            test_list = pickle.load(f)
    else:
        train_list, test_list = get_train_test_list(user_trajectory_dict)
        with open(temp_train_list_file_path, 'wb') as f:
            pickle.dump(train_list, f)
        with open(temp_test_list_file_path, 'wb') as f:
            pickle.dump(test_list, f)
        
    # 生成训练csv和测试csv
    df = pd.concat([pd.DataFrame.from_dict(x, orient='index').T for x in train_list], ignore_index=False)
    df.sort_values(by=['local_time'], ascending=True, inplace=True)
    df.to_csv(os.path.join(region_dir, region+'_train.csv'), index=False)
    df = pd.concat([pd.DataFrame.from_dict(x, orient='index').T for x in test_list], ignore_index=False)
    df.sort_values(by=['local_time'], ascending=True, inplace=True)
    df.to_csv(os.path.join(region_dir, region+'_test.csv'), index=False)

