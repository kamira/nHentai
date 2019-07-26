# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import yaml
import os
import re
import shutil

current_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(current_dir, 'downloader')

base_url = "https://nhentai.net/g"

class Info:
    def __init__(self, id):
        self.id = id
        self.url = '{}/{}/'.format(base_url, id)
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        info_block = soup.find(id="info")
        title = info_block.find('h1')
        self.eng_title = title.get_text()
        title = info_block.find('h2')
        self.raw_title = title.find(text=True, recursive=False).strip()
        print(self.raw_title)
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
        print(info_block)
        return info_block


class PictureDownloader:
    def __init__(self, url, filepath, page):
        self.reg = r'(.*\/)\d*\.(.*)'
        self.url = url
        self.filepath = filepath
        self.page = page + 1
    def download(self):
        url = '{}1/'.format(self.url)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        p = soup.find('section', id='image-container')
        p = p.find('img').attrs['src']
        picture = re.match(self.reg, p)
        for i in range(self.page):
            pic_path = os.path.join(self.filepath, '{}.{}'.format(i, picture.group(2)))
            pic_url = '{}{}.{}'.format(picture.group(1), i, picture.group(2))
            print(pic_path, pic_url)
            r = requests.get(pic_url)
            if r.status_code == 200:
                with open(pic_path, 'wb') as f:
                    f.write(r.content)

for i in range(1, 1000):
    try:
        x = Info(i)
        current_path = os.path.join(path, str(i))
        tmp = x.render_info()
        if not os.path.exists(current_path):
            os.makedirs(current_path)
        with open(os.path.join(current_path, 'info.yaml'), 'w') as f:
            yaml.dump(tmp, f, allow_unicode=True)
        a = PictureDownloader(tmp['url'], current_path, tmp['page'])
        a.download()
    except Exception:
        continue