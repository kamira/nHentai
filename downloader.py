# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import yaml
import os
import re
from multiprocessing import Pool
import random

FILE_EXT = ['png', 'jpg', 'jpeg', 'bmp']
base_url = "https://nhentai.net/g"


class Info:
    def __init__(self, id):
        self.id = id
        self.url = '{}/{}/'.format(base_url, id)
        i = 0
        while True:
            i = i + 1
            r = requests.get(self.url)
            if r.status_code == 200:
                break
            else:
                print('[{}] Bonbon information Retry: {}'.format(r.status_code, i+1))
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


def get_info_job(i, path):

    def picture_download_job(url, file_path, page, title):

        def download(d_path, d_url):
            times = 0
            while True:
                times = times + 1

                if times % 10 == 0:
                    raw_url = re.match(r'(.*)\.\w$', d_url)
                    d_url = '{}.{}'.format(raw_url.group(1), random.choice(FILE_EXT))
                r = requests.get(d_url)
                if r.status_code == 200:
                    with open(d_path, 'wb') as f:
                        f.write(r.content)
                    break
                else:
                    print('[ERROR] {} - Picture Download Retry: {}\n'.format(r.status_code, times+1))

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
            download(pic_path, pic_url)
            print("[Progress] {} | Download: {}/{}".format(i, title, page+1))
        #     pool2.apply(download, (pic_path, pic_url,))
        # pool2.close()
        # pool2.join()


    x = Info(i)
    current_path = os.path.join(path, str(i))
    tmp = x.render_info()
    if not os.path.exists(current_path):
        os.makedirs(current_path)
    with open(os.path.join(current_path, 'info.yaml'), 'w', encoding='utf-8') as f:
        yaml.dump(tmp, f, allow_unicode=True)
        print("[Progess] {}".format(tmp['raw_title']))
    picture_download_job(tmp['url'], current_path, tmp['page'], tmp['raw_title'])
    print("[Finished] {}".format(tmp['raw_title']))


def download_start(start_id, end_id, path):



    pool = Pool()
    for i in range(start_id, end_id+1):
        pool.apply_async(get_info_job, (i, path,))
    pool.close()
    pool.join()


def main():
    print("nHentai 陽春下載器\n/_/_/_/_/_/_/_/_/_/_/_\n")
    print("ID 範例為: https://nhentai/g/****/\n米字部分即為ID\n")
    start = ""
    end = ""
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
    download_start(start, end, path_input)


if __name__ == '__main__':
    main()
