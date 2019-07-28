# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup
import yaml
import os
import re
from multiprocessing import Pool
from multiprocessing import freeze_support
import multiprocessing
import random
import datetime
import time
from multiprocessing.pool import ThreadPool



class nHentaiInfo:
    def __init__(self, id):
        self.id = id
        self.url = f"https://nhentai.net/g/{id}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
            # 'Authority': 'nhentai.net',
            # 'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            # "upgrade-insecure-requests": "1",
            "Cache-Control": "max-age=0",
            "scheme": "https"
        }
        api_url = f"https://nhentai.net/api/gallery/{id}"
        while True:
            time.sleep(1)
            # print(api_url)
            r = requests.get(api_url, headers=headers)
            r.encoding = 'utf-8'
            if r.status_code == 403:
                self.alive = False
                break
            if r.status_code == 200:
                self.alive = True
                data = r.json()
                # Title
                self.title = data['title']
                # Tag
                self.tag_dict = {}
                for tag_item in data['tags']:
                    if tag_item['type'] in self.tag_dict:
                        self.tag_dict[tag_item['type']].append(tag_item['name'])
                    else:
                        self.tag_dict[tag_item['type']] = [tag_item['name']]
                # Page Size
                self.pages = data['num_pages']
                self.pages_infomation = data['images']['pages']
                # Media ID
                self.media_id = data['media_id']
                break

    def get_media_list(self):
        file_ext_mapping_list = {"j": "jpg", "p": "png", "g": "gif", "b": "bmp", "s": "svg", "a": "apng", "m": "mp4"}
        media_list = []
        for i in range(len(self.pages_infomation)):
            file_ext = file_ext_mapping_list[self.pages_infomation[i]['t']]
            source = f"https://i.nhentai.net/galleries/{self.media_id}/{i+1}.{file_ext}"
            target = f"{i+1}.{file_ext}"
            media_list.append({"source": source, "target": target, "page_no": i+1})
        return media_list

    def get_information(self):
        return {
            "id": self.id,
            "media_id": self.media_id,
            "title": self.title,
            "category": self.tag_dict,
            "page": self.pages,
            "url": self.url
        }


def save_infomation_file(file_type, raw, path):
    file_type = file_type.lower()
    # Check folder is exists
    if not os.path.exists(path):
        os.makedirs(path)
    # Dump to JSON
    if file_type == "json":
        with open(os.path.join(path, 'info.json'), 'w', encoding='utf-8') as f:
            json.dump(u"ברי צקלה", f, ensure_ascii=False)
    # Dump to yaml
    if file_type == "yaml":
        with open(os.path.join(path, 'info.yaml'), 'w', encoding='utf-8') as f:
            yaml.dump(raw, f, allow_unicode=True)
    print("{:>10} {:>5} {:<50} {:>10} {:>10}".format("[information]", raw['id'], raw['title']['japanese'], "information", "saved"))
    return True


def download_pic(d_path, d_name, target_id, title, page_no, page_total):
    # try:

    page = f"{page_no}/{page_total}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
    }
    if os.path.exists(d_name):
        print("{:>10} {:>5} {:<50} {:>10} {:>10}".format("[information]", target_id, title,
                                                          "pass", page))
        return True
    while True:
        time.sleep(random.random())
        r = requests.get(d_path, headers=headers)
        if r.status_code == 200:
            with open(d_name, 'wb') as f:
                f.write(r.content)
            print("{:>10} {:>5} {:<50} {:>10} {:>10}".format("[information]", target_id, title,
                                                             "saved", page))
            break
        else:
            print("{:>10} {:>5} {:<50} {:>10} {:>10}".format("[error]", target_id, title,
                                                             "retry", page))
    return True
    # except Exception as e:
    #     print(str(e))

if __name__ == '__main__':
    freeze_support()

    def download_start(start_id, end_id, path, pool_size, file_typename):
        pool = ThreadPool(pool_size)
        for i in range(start_id, end_id+1):
            s = nHentaiInfo(i)
            if s.alive:
                information = s.get_information()
                new_path = os.path.join(path, str(i))
                media_list = s.get_media_list()
                for j in media_list:
                    pic_new_path = os.path.join(new_path, j['target'])
                    # print(j['source'])
                    pool.apply_async(download_pic, (j['source'], pic_new_path, information['id'], information['title']['japanese'], j['page_no'], information['page'],))
                pool.apply_async(save_infomation_file, (file_typename, information, new_path,))
        pool.close()
        pool.join()

    def main():
        threadpool_size = multiprocessing.cpu_count()
        now = datetime.datetime.now()
        print("Copyright (c) {} Harutsuki All Rights Reserved.\n".format(now.year))
        print("{:^40}".format("nHentai 陽春下載器 v1.4.2\n"))
        print("{:^40}".format("============ Information ==========="))
        print("{:>30} : {}".format("CPU Core", multiprocessing.cpu_count()))
        print("{:>30} : {}\n".format("Default threads setting", threadpool_size))

        thread_size = ""
        while not thread_size.isdigit():
            thread_size = input("Change thread :")
            if thread_size.isdigit():
                threadpool_size = int(thread_size)
                break
            else:
                break
        start = ""
        end = ""
        current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'download')
        typename = "yaml"
        while not start.isdigit():
            start = input("Start no. :")
            if start.isdigit():
                start = int(start)
                break
            else:
                print('Please enter a number')
        while not end.isdigit():
            end = input("End no. :")
            if end.isdigit():
                end = int(end)
                break
            else:
                print('Please enter a number')
        print("Default saved path is {}".format(current_dir))
        path_input = input("Change path:")
        if path_input == "":
            path_input = current_dir
            if not os.path.exists(path_input):
                os.makedirs(path_input)
        while True:
            print('Output: json, yaml')
            new_typename = input("Type :")
            if new_typename.lower() in ['json', 'yaml', '']:
                if new_typename != "":
                    typename = new_typename
                break
        download_start(start, end, path_input, threadpool_size, typename)

    main()
