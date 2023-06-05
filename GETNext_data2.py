# Author: S_Peng(create), S_Sun(modify)

# -*- coding:utf-8 -*-
from datetime import datetime,timedelta
from numpy import *
import csv
import uuid
def load_data(filepath,tzone):
    file=open(filepath,"r",encoding='utf-8')
    data=[]
    user_id=[]
    POI_catid = []
    local_time=[]
    i=0
    for line in file:
        i=i+1
        #print(i)
        text=line.strip()
        text_list=text.split("\t")
        t=datetime.strptime(text_list[5], '%Y-%m-%d %H:%M:%S')
        #text_list[6].encode('unicode-escape').decode('utf-8')
        POI_catid = str(uuid.uuid3(uuid.NAMESPACE_DNS, text_list[3]))
        POI_catid = ''.join(POI_catid.split('-'))
        #text_list.append(t)
        local_time.append(t)
        #text_list[5] = t
        text_list.append(POI_catid)
        text_list[1], text_list[4], text_list[5], text_list[3], text_list[0], text_list[6], text_list[7], text_list[2] = \
        text_list[0], text_list[1], text_list[2], text_list[3], text_list[4], text_list[5],text_list[6], text_list[7],#有评论数据
        text_list.append(t.weekday())
        a = t.hour / 24 * 48
        if t.minute < 30:
            a = a
        else:
            a += 1
        norm_in_day_time = a / 48
        # norm_in_day_time.append(norm_in)
        text_list.append(norm_in_day_time)
        data.append(text_list)
        #local_time.append(t)
        user_id.append(text_list[0])
    return data, user_id, local_time
"""
    user_id_new = []
    User_id_new = []
    user_list ={}
    for i in range(0, len(data)):
        user_id_item = data[i][0]
        if user_id_item not in user_list.keys():
            user_list[user_id_item] = i
            i=i+1
        else:
            user_list = user_list

    for i in range(0, len(data)):
        user_id_item = data[i][0]
        if user_id_item not in user_list.keys():
            user_list[user_id_item] = i
            i=i+1
            user_id_new.append(user_list[user_id_item])
        else:
            user_id_new.append(user_list[user_id_item])
        data[i].insert(0, user_list[user_id_item])
        data[i].pop(1)
        User_id_new.append(str(data[i][0]))
    return data, User_id_new, local_time
"""

def update_id2index(id2index):
    train={}
    test={}
    for key,value in id2index.items():
        sorted_index_trajectory=[]
        trajectory = []
        max_time_delta=timedelta(hours=24)
        start_time=value[0][1]
        trajectory_id=1
        temp=[[value[0][0],key+'_'+str(trajectory_id)]]
        for (index,time) in sorted(value, key=lambda x:x[1])[1:]:
            time_delta=time-start_time
            if time_delta>max_time_delta:
                trajectory_id+=1
                #temp=[]
            start_time=time
            temp.append([index,key+'_'+str(trajectory_id)])
        length=len(temp)
        train_value=[]
        test_value=[]

        for i in range(len(temp)):
            if i<ceil(length*0.8):
                train_value.append(temp[i])
            else:
                test_value.append(temp[i])

        train[key]=train_value
        test[key]=test_value
    return train,test

def get_train_test(user_id,local_time):
    id2index={}
    user_id_all = user_id
    for i,(user_id,local_time) in enumerate(zip(user_id,local_time)):
        value =(i,local_time)
        if user_id not in id2index:
            id2index[user_id] = [value]
        else:
            id2index[user_id].append(value)

    train,test=update_id2index(id2index)
    return train,test

def insert_poicode_train(data):
    POI_catid_code = []
    poi_code = {}
    k = 1
    for i in range(0, len(data)):
        POI_catname = data[i][3]
        if POI_catname not in poi_code.keys():
            poi_code[POI_catname] = k
            k = k + 1
        else:
            poi_code = poi_code


    for i in range(0, len(data)):
        POI_catname = data[i][3]
        if POI_catname not in poi_code.keys():
            poi_code[POI_catname] = k
            k = k+ 1
            POI_catid_code.append(poi_code[POI_catname])
        else:
            POI_catid_code.append(poi_code[POI_catname])
        data[i].insert(3, poi_code[POI_catname])
    return data,  poi_code

def insert_poicode_test(data, poi_code):
    POI_catid_code =[]
    poi_code = poi_code
    k=len(poi_code)

    for i in range(0, len(data)):
        POI_catname=data[i][3]
        if POI_catname in poi_code.keys():
            POI_catid_code.append(poi_code[POI_catname])
        else:
            k = k + 1
            poi_code[POI_catname] = k
            POI_catid_code.append(k)
        data[i].insert(3, poi_code[POI_catname])
    return data

def update_data(data,id2index):
    result=[]

    for value in id2index.values():
        for (i,trajectory_id) in value:
            data[i].append(trajectory_id)
            #data[i].append(rand)
            result.append(data[i])
            #result.append(data[index]+[trajectory_id,rand])
    return result

if __name__=='__main__':
    head=["user_id","POI_id","POI_catid", "POI_catid_code", "POI_catname", "latitude","longitude","time","text","day_of_week","norm_in_day_time","trajectory_id"]#评论
    #head = ["user_id", "POI_id", "POI_catid", "POI_catid_code", "POI_catname", "latitude", "longitude", "time", "day_of_week", "norm_in_day_time", "trajectory_id", "rand"]
    data,user_id,localtime=load_data(r"./dataset/Hawaii/Hawaii.csv",'Asia/Shanghai')
    train,test=get_train_test(user_id,localtime)

    #在训练集和测试集添加trajectory_id列
    train =update_data(data,train)
    test =update_data(data,test)

    #在训练集和测试集添加poi_code
    train, poi_code = insert_poicode_train(train)
    test = insert_poicode_test(test, poi_code)

    # 对训练集和测试集按照time重新排序
    train.sort(key=lambda x:x[7])
    test.sort(key=lambda x:x[7])

    print(type(train))


    with open(r'./dataset/Hawaii/Hawaii_train.csv', 'w', encoding='utf-8', newline='') as fp:
        writer = csv.writer(fp)
        writer.writerow(head)
        writer.writerows(train)
    with open(r'./dataset/Hawaii/Hawaii_test.csv', 'w', encoding='utf-8', newline='') as fp:
        writer = csv.writer(fp)
        writer.writerow(head)
        writer.writerows(test)
