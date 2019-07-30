import yaml
import os
from multiprocessing import freeze_support
from multiprocessing.pool import ThreadPool
import multiprocessing
from hentai import nHentai
import time
import random
import requests
import datetime
import json
import logging
import sys


LOG_LEVEL = logging.INFO
FORMAT = "[%(asctime)s] Level: %(levelname)-8s File: %(filename)-20s Func: %(funcName)-30s Line: %(lineno)-10d" \
         " Message: %(message)s"
LOG_FORMAT = logging.Formatter(FORMAT)
log = logging.getLogger("Hentai")
log.setLevel(LOG_LEVEL)

CH = logging.StreamHandler(sys.stdout)
CH.setLevel(LOG_LEVEL)
CH.setFormatter(LOG_FORMAT)
log.addHandler(CH)

headers: dict = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/75.0.3770.142 '
                  'Safari/537.36'
}
default_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'donwload')

if __name__ == '__main__':
    freeze_support()

    def main_download(start_: int, end_: int, path_: str, size_: int, info_: str):
        try:
            pool = ThreadPool(size_)
            for i in range(start_, end_ + 1):
                h = nHentai(i)
                if h.live():
                    pool.apply_async(save_info, (h.info(), path_, info_,))
                    task_list = h.download_task_render(path_)
                    [pool.apply_async(download_pic, task_) for task_ in task_list]
            pool.close()
            pool.join()
        except KeyboardInterrupt:
            exit(0)

    def download_pic(id_: int, url_: str, path_: str, title_:str, page_: int, total_: int):
        log.info(f"Download ({page_}/{total_}): {title_} {url_}")
        if os.path.exists(path_):
            return True
        else:
            while True:
                time.sleep(random.random())
                r = requests.get(url_, headers=headers)
                status = r.status_code
                if status == 200:
                    with open(path_, 'wb') as f:
                        f.write(r.content)
                    break
                else:
                    log.warning(
                        f"HTTP_STATUS: {status}. Gallery {id_} page {page_}/{total_} in {title_} failed to download. "
                        f"Retry in 1 sec. {url_}")
                    time.sleep(1)
            return True

    def save_info(info_: dict, path_: str, file_type_: str):
        file_type_ = file_type_.lower()
        path_ = os.path.join(path_, str(info_['id']))
        if not os.path.exists(path_):
            os.makedirs(path_)
        with open(os.path.join(path_, f"info.{file_type_}"), 'w', encoding='utf-8') as f:
            if file_type_ == "json":
                json.dump(info_, f, ensure_ascii=False)
            elif file_type_ == "yaml":
                yaml.dump(info_, f, allow_unicode=True)

            log.info(f"Save {info_['title']['japanese']} information is completed. {path_}")
        return True

    def check_input(prompt: str, type_: type):
        while True:
            try:
                input_ = type_(input(prompt))
                return input_
            except ValueError:
                print('Unacceptable input, please check it.')

    def main():
        now = datetime.datetime.now()
        print("Copyright (c) 2019-{} Harutsuki All Rights Reserved.\n".format(now.year))
        print("nHentai Downloader v1.4.3")
        pool_size = check_input('Enter thread pool size: ', int)
        if pool_size < 1:
            pool_size = multiprocessing.cpu_count() * 3
        start_no = check_input('Enter start no. ', int)
        end_no = check_input('Enter end no. ', int)
        while True:
            info_type = check_input('Infomation file type(json, yaml) ', str)
            if info_type == "":
                info_type = 'yaml'
                break
            if info_type.lower() in ['json', 'yaml']:
                break
            else:
                print(f"{info_type} is unacceptable")
        dir_path = check_input(f'Input download location \n (default: {default_path}): ', str)
        if dir_path == "":
            dir_path = default_path
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        main_download(start_no, end_no, dir_path, pool_size, info_type)

    main()

