# -*- coding: utf-8 -*-
import requests
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

FILE_EXT = ['png', 'jpg', 'jpeg', 'bmp']
base_url = "https://nhentai.net/g"

url_list = []


class Info:
    def __init__(self, id, retry):
        self.id = id
        self.url = '{}/{}/'.format(base_url, id)
        i = 0
        while True:
            i = i + 1
            time.sleep(random.choice([i for i in range(20)]))
            r = requests.get(self.url)
            if r.status_code == 200:
                self.alive = True
                break
            else:
                print('[{}] Bonbon information Retry: {}'.format(r.status_code, i+1))
            if int(retry) > 0:
                if i >= int(retry):
                    self.alive = False
                    break
        if self.alive:
            soup = BeautifulSoup(r.text, "html.parser")
            info_block = soup.find(id="info")
            title = info_block.find('h1')
            self.eng_title = title.get_text()
            title = info_block.find('h2')
            self.raw_title = title.find(text=True, recursive=False).strip()
            # print(self.raw_title)
            tag_all = info_block.find_all('div', class_='tag-container')
            self.tag_dict = {}
            self.page = len(soup.find_all('a', class_='gallerythumb'))
            for i in range(len(tag_all)):
                x = tag_all[i].find(text=True, recursive=False).strip().replace(':', "")
                sub_tag = tag_all[i].find_all("a")
                y = [j.find(text=True, recursive=False).strip() for j in sub_tag]
                self.tag_dict[x] = y

    def render_info(self):
        info_block = {
            "id": self.id,
            "url": self.url,
            "eng_title": self.eng_title,
            "raw_title": self.raw_title,
            "category": self.tag_dict,
            "page": self.page
        }
        return info_block


def download(d_path, d_url, d_title, d_p, d_total):
    # print(d_path, d_url)
    reg_file_ext = r'(.*)\.\w*$'
    times = 0
    while True:
        times = times + 1
        if times % 5 == 0:
            raw_url = re.match(reg_file_ext, d_url)
            raw_path = re.match(reg_file_ext, d_path)

            fileext = random.choice(FILE_EXT)
            d_url = '{}.{}'.format(raw_url.group(1), fileext)
            d_path = '{}.{}'.format(raw_path.group(1), fileext)
        time.sleep(random.choice([i for i in range(20)]))
        r = requests.get(d_url)
        if r.status_code == 200:
            with open(d_path, 'wb') as f:
                f.write(r.content)
            break
        else:
            print('[ERROR] {} - Picture Download Retry: {}'.format(r.status_code, times + 1))
    print("[Progress] {} | Download: {}/{}".format(d_title, d_p, d_total))


def get_info_job(i, path, retry):
    def picture_download_job(url, file_path, page, title):
        reg = r'(.*\/)\d*\.(.*)'
        url = '{}1/'.format(url)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        p = soup.find('section', id='image-container')
        p = p.find('img').attrs['src']
        picture = re.match(reg, p)
        # pool2 = Pool(2)
        for i in range(1, page + 1):
            pic_path = os.path.join(file_path, '{}.{}'.format(i, picture.group(2)))
            pic_url = '{}{}.{}'.format(picture.group(1), i, picture.group(2))
            # pool2.apply_async(download, (pic_path, pic_url, title, i, page+1,))
            # url_list.append((pic_path, pic_url, title, i, page+1,))
            download(pic_path, pic_url, title, i, page)

    x = Info(i, retry)
    if x.alive:
        current_path = os.path.join(path, str(i))
        tmp = x.render_info()
        if not os.path.exists(current_path):
            os.makedirs(current_path)
        with open(os.path.join(current_path, 'info.yaml'), 'w', encoding='utf-8') as f:
            yaml.dump(tmp, f, allow_unicode=True)
            print("[Progress] {}".format(tmp['raw_title']))
        picture_download_job(tmp['url'], current_path, tmp['page'], tmp['raw_title'])
        print("[Finished] {}".format(tmp['raw_title']))
    print('[ERROR] {} | Alive?'.format(x.url))


if __name__ == '__main__':
    freeze_support()

    def download_start(start_id, end_id, path, ret):
        # pool = Pool()
        pool = ThreadPool(multiprocessing.cpu_count() * 20)
        for i in range(start_id, end_id+1):
            pool.apply_async(get_info_job, (i, path, ret, ))
            # get_info_job(i, path, ret)
        # pool2.close()
        # pool2.join()
        pool.close()
        pool.join()
        # [pool.apply_async(download, i) for i in url_list]



    def main():
        now = datetime.datetime.now()
        print("Copyright (c) {} Harutsuki All Rights Reserved.\n".format(now.year))
        print("nHentai 陽春下載器 v1.0\n")
        print("Information ===========")
        print("CPU 核心數: {}".format(multiprocessing.cpu_count()))
        print("預計建立線程數量: {}\n".format(multiprocessing.cpu_count() * 20))

        start = ""
        end = ""
        ret = ""
        current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'download')

        while not start.isdigit():
            start = input("請輸入起始的ID:")
            if start.isdigit():
                start = int(start)
                break
            else:
                print('請輸入數字，ID為一串數字')
        while not end.isdigit():
            end = input("請輸入結束的ID:")
            if end.isdigit():
                end = int(end)
                break
            else:
                print('請輸入數字，ID為一串數字')
        print("預設儲存路徑為 {}".format(current_dir))
        path_input = input("請輸入新的儲存路徑，不輸入則使用預設路徑:")
        if path_input == "":
            path_input = current_dir
            if not os.path.exists(path_input):
                os.makedirs(path_input)
        while not ret.isdigit():
            ret = input("可接受本子重試次數(0為無限):")
            if ret == "":
                ret = "0"
            if ret.isdigit():
                ret = int(ret)
                break
            else:
                print('請輸入數字，ID為一串數字')

        download_start(start, end, path_input, ret)

    main()
