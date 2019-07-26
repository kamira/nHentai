# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import yaml
import os
import re
from multiprocessing import Pool
import time

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


def get_info_job(i):

    def picture_download_job(url, file_path, page):

        def download(d_path, d_url):
            r = requests.get(d_url)
            print(d_url, d_path)
            if r.status_code == 200:
                with open(d_path, 'wb') as f:
                    f.write(r.content)

        reg = r'(.*\/)\d*\.(.*)'
        url = '{}1/'.format(url)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        p = soup.find('section', id='image-container')
        p = p.find('img').attrs['src']
        picture = re.match(reg, p)
        # pool2 = Pool(2)
        for i in range(page + 1):
            pic_path = os.path.join(file_path, '{}.{}'.format(i, picture.group(2)))
            pic_url = '{}{}.{}'.format(picture.group(1), i, picture.group(2))
            download(pic_path, pic_url)
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
    print(tmp['raw_title'])
    picture_download_job(tmp['url'], current_path, tmp['page'])


def main():
    pool = Pool()
    for i in range(1, 1000):
        try:
            pool.apply_async(get_info_job, (i,))
            # thread = threading.Thread(target=get_info_job, args=(i,))  # 定义线程
            # thread.start()  # 让线程开始工作
        except Exception:
            continue
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()









