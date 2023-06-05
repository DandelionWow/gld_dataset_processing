# Author: S_Peng(create), S_Sun(modify)

import json
import pandas as pd
import numpy as np
from datetime import datetime
import re
import emoji

reviews_path='./dataset/Hawaii/review-Hawaii_10.json'
file1 = open(reviews_path, 'r', encoding="utf-8")
papers = []
user_id = []
time = []
gmap_id = []
review= []
pics = []
for line in file1:
    js = json.loads(line)

    # 只保留出2018和2019年的
    if datetime.fromtimestamp(int(js['time']/1000)).year not in [2018, 2019]:
        continue

    text = js['text']
    if text == None:
        text = text
    else:
        text = emoji.replace_emoji(text, replace='aaaa')

    user_id.append(js['user_id'])
    time.append(js['time'])
    gmap_id.append(js['gmap_id'])
    review.append(text)#评论
    #pics.append(js['pics'])

df1 = pd.DataFrame({'user_id':user_id, 'time':time, 'gmap_id':gmap_id, 'text':review})#评
time = df1['time'].astype(np.int64)
ntime= pd.to_datetime(df1['time'].map(lambda x:datetime.fromtimestamp(int(x/1000)).strftime('%Y-%m-%d %H:%M:%S')))

print(len(df1))
df1 = pd.DataFrame({'user_id':user_id, 'time':ntime, 'gmap_id':gmap_id, 'text':review})
#df1 = pd.DataFrame({'user_id':user_id, 'time':ntime, 'gmap_id':gmap_id})
df11 = df1.drop_duplicates(subset=['user_id','time', 'text'],keep=False,inplace=False)
#df11 = df1.drop_duplicates(subset=['user_id','time'],keep=False,inplace=False)
print(len(df11))

meta_path=r'./dataset/Hawaii/meta-Hawaii.json'
file2 = open(meta_path, 'r', encoding="utf-8")
gmap_id = []
latitude = []
longitude = []
category = []

for line in file2:
    #line = remove_invalid_escapes(line)
    js = json.loads(line)
    gmap_id.append(js['gmap_id'])
    latitude.append(js['latitude'])
    longitude.append(js['longitude'])
    category.append((js['category']))
    #category.append(re.sub(r"[\([{})\]]", "",str(js['category'])))
df2 = pd.DataFrame({'gmap_id':gmap_id, 'latitude':latitude, 'longitude':longitude, 'category':category})
df2 = df2.drop_duplicates(['gmap_id'])
data = pd.merge(df2,df11, on='gmap_id', how='inner')
print(len(data))

data1 = data.replace('\n', '', regex=True)
data1 = data1.replace('\t', '', regex=True)

data2 = data1.replace('', 'None')

data2 = data2.dropna(how='any')#如果某一列存在缺失值，则删除整行
data2 = data2.sort_values(by='time')

print(len(data2))

data2.to_csv(r'./dataset/Hawaii/Hawaii.csv', index=False, header=None, sep='\t')
