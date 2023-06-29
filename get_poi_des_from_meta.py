import argparse
import json
import os

class MISC_Template:
    def __init__(self):
        self.str_getting_here = 'Getting here'
        self.str_service_options = 'Service options'
        self.str_popular_for = 'Popular for'
        self.str_offerings = 'Offerings'
        self.str_lodging_options = 'Lodging options'
        self.str_amenities = 'Amenities'
        self.str_activities = 'Activities'
        self.str_planning = 'Planning'
        self.str_health_and_safety = 'Health & safety' # Health and safety
        self.str_dining_options = 'Dining options'
        self.str_crowd = 'Crowd'
        self.str_highlights = 'Highlights'
        self.str_payments = 'Payments'
        self.str_atmosphere = 'Atmosphere'
        self.str_recycling = 'Recycling'
        self.str_accessibility = 'Accessibility'
        self.str_from_the_business = 'From the business'
        
    def __append_str(self, str, list):
        for i, s in enumerate(list):
            str += s
            if (i + 1) != len(list):
                str += ', '
        return str

    def __append_str_has_and(self, str, list):
        for i, s in enumerate(list):
            str += s
            if (i + 2) < len(list):
                str += ', '
            if (i + 2) == len(list):
                str += ' and '
        return str

    def __is_or_are(self, list):
        if len(list) > 1:
            return 'are'
        else:
            return 'is'
    
    def getting_here(self, list):
        if list is None:
            return ''
        return 'This place has 24-hour public transportation service. '
    
    def service_options(self, list):
        if list is None:
            return ''
        
        str = 'We provide '
        str = self.__append_str(str, list)
        str += ' services. '
        return str
    
    def popular_for(self, list):
        if list is None:
            return ''
        
        str = 'Our '
        str = self.__append_str(str, list)
        str += ' ' + self.__is_or_are(list)
        str += ' popular. '
        return str
    
    def offerings(self, list):
        if list is None:
            return ''
        
        str = 'We can offer '
        str = self.__append_str_has_and(str, list)
        str += '. '
        return str
    
    def lodging_options(self, list):
        if list is None:
            return ''
        
        str = 'This place offers several lodging options such as '
        str = self.__append_str(str, list) # 不加etc了
        str += '. '
        return str
    
    def amenities(self, list):
        if list is None:
            return ''
        
        str = 'This place offers several amenities such as '
        str = self.__append_str(str, list) # 不加etc了
        str += '. '
        return str
    
    def activities(self, list):
        if list is None:
            return ''
        
        str = 'We have '
        str = self.__append_str_has_and(str, list)
        str += ' activites. '
        return str
    
    def planning(self, list):
        if list is None:
            return ''
        
        str = 'Our service category is '
        str = self.__append_str_has_and(str, list)
        str += '. '
        return str
    
    def health_and_safety(self, list):
        if list is None:
            return ''
        
        str = 'The health and safety standards here include: '
        str = self.__append_str_has_and(str, list)
        str += '. '
        return str
    
    def dining_options(self, list):
        if list is None:
            return ''
        
        str = 'We offer options for '
        str = self.__append_str(str, list) # 不加and more了
        str += '. '
        return str
    
    def crowd(self, list):
        if list is None:
            return ''
        
        str = 'Our place is suitable for '
        str = self.__append_str_has_and(str, list) # 不加and so on了
        str += '. '
        return str

    def highlights(self, list):
        if list is None:
            return ''
        
        str = 'We have many highlights here, such as '
        str = self.__append_str(str, list)
        str += '. '
        return str
    
    def from_the_business(self, list):
        if list is None:
            return ''
        
        str = 'This place '
        str = self.__append_str_has_and(str, list)
        str += '. '
        return str
    
    def accessibility(self, list):
        if list is None:
            return ''
        
        str = 'We have '
        str = self.__append_str(str, list)
        str += '. '
        return str
    
    def recycling(self, list):
        if list is None:
            return ''
        
        str = ''
        str = self.__append_str_has_and(str, list)
        str += ' can be recycled here. '
        return str
    
    def atmosphere(self, list):
        if list is None:
            return ''
        
        str = 'The atmosphere here is '
        str = self.__append_str_has_and(str, list)
        str += '. '
        return str
    
    def payments(self, list):
        if list is None:
            return ''
        
        str = 'The payment methods supported here are '
        str = self.__append_str(str, list)
        str += '. '
        return str
    

if __name__ == "__main__" :
    # paremeters
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_path', type=str, default='./datasets', help='the path of the dataset')
    parser.add_argument('--region', type=str, default='Alaska', help='the region name of datasets(e.g. California)')
    args, _ = parser.parse_known_args()

    # path设置
    parent_path = os.path.join(args.dataset_path, args.region)
    if not os.path.exists(parent_path):
        os.mkdir(parent_path)
    meta_file_path = os.path.join(parent_path, 'meta-' + args.region + '.json')
    pois_description_file_path = os.path.join(parent_path, 'pois_description.json')

    # 初始化类
    template = MISC_Template()

    # 打开meta-xxx.json文件
    meta_file = open(meta_file_path, 'r')
    # 打开poi_description_file文件
    pois_description_file = open(pois_description_file_path, 'w')
    
    # 遍历meta-xxx.json，row_i为行号，line为一行数据
    for row_i, line in enumerate(meta_file):
        # 解析json对象，得到字典
        obj = json.loads(line)

        # 取出obj.gmap_id和obj.MISC和description
        gmap_id = obj['gmap_id'].replace(":", "-")
        misc_info = obj['MISC']
        description = obj['description']

        # 定义总字符串
        poi_des = ''
        # 追加description
        if description is not None:
            poi_des += description + ' '
        # 模板处理MISC information，并将结果追加到poi_des
        if misc_info is not None:
            poi_des += template.accessibility(misc_info.get(template.str_accessibility))
            poi_des += template.service_options(misc_info.get(template.str_service_options))
            poi_des += template.amenities(misc_info.get(template.str_amenities))
            poi_des += template.activities(misc_info.get(template.str_activities))
            poi_des += template.atmosphere(misc_info.get(template.str_atmosphere))
            poi_des += template.crowd(misc_info.get(template.str_crowd))
            poi_des += template.dining_options(misc_info.get(template.str_dining_options))
            poi_des += template.from_the_business(misc_info.get(template.str_from_the_business))
            poi_des += template.health_and_safety(misc_info.get(template.str_health_and_safety))
            poi_des += template.highlights(misc_info.get(template.str_highlights))
            poi_des += template.lodging_options(misc_info.get(template.str_lodging_options))
            poi_des += template.offerings(misc_info.get(template.str_offerings))
            poi_des += template.payments(misc_info.get(template.str_payments))
            poi_des += template.popular_for(misc_info.get(template.str_popular_for))
            poi_des += template.planning(misc_info.get(template.str_planning))
            poi_des += template.recycling(misc_info.get(template.str_recycling))
            poi_des += template.getting_here(misc_info.get(template.str_getting_here))

        # 跳过空串，最后填充0向量
        if poi_des == '':
            continue

        # 保存转换结果
        obj = {str(row_i+1)+'_'+gmap_id: poi_des} # 与image des和review summary保存格式一致
        pois_description_file.write(json.dumps(obj) + '\n')
        pois_description_file.flush()

    meta_file.close()
    pois_description_file.close()