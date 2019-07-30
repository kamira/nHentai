import requests
import time
import random
import itertools
from datetime import datetime
import os
import logging

log = logging.getLogger("Hentai")

headers: dict = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/75.0.3770.142 '
                  'Safari/537.36'
}
file_ext_map: dict = {"j": "jpg", "p": "png", "g": "gif", "b": "bmp", "s": "svg", "a": "apng", "m": "mp4"}


class nHentai():
    def __init__(self, id_: int):
        self.__id: int = int(id_)
        self.__url: str = f"https://nhentai.net/g/{str(id_)}"
        self.__api: str = f"https://nhentai.net/api/gallery/{str(id_)}"
        self.__info: dict = dict()
        self.__meta: dict = dict()
        self.__alive: bool = True
        self.__get_information()

    def __get_information(self):

        def extract_key(v: dict):
            return v['type']

        count: int = 0
        while self.__alive:
            time.sleep(random.random())
            r = requests.get(self.__api, headers=headers)
            r.encoding = 'utf-8'
            status = r.status_code
            if count > 3:
                self.__alive = False
                log.warning(f"HTTP_STATUS: {status}."
                            f" Discard this gallery. {self.__url}")
                continue
            if r.status_code == 200:
                self.__meta = r.json()
                log.info(f"Download gallery {self.__id} information from {self.__url}")
                break
            else:
                log.warning(f"HTTP_STATUS: {status}. Gallery {self.__id} information failed to download. "
                            f"Retry in 1 seconds. Retries: {count}/3")
                count += 1
                time.sleep(1)

        if self.__alive:
            self.__info: dict = {
                "id": self.__meta['id'],
                "title": self.__meta['title'],
                'category': [{k: [x["name"] for x in g]}
                             for k, g in itertools.groupby(self.__meta["tags"], extract_key)],
                'upload_date': {
                    "key": self.__meta['upload_date'],
                    "key_as_string": datetime.utcfromtimestamp(self.__meta['upload_date']).strftime('%Y-%m-%dT%H:%M:%SZ')
                },
                'media_id': self.__meta['media_id'],
                'num_pages': self.__meta['num_pages'],
                'pages': [{"page": i+1, "file_ext": j['t']} for i, j in enumerate(self.__meta["images"]['pages'])],
                'url': self.__url
            }
    def info(self):
        return self.__info
    def pic_url(self):
        return ["https://i.nhentai.net/galleries/{}/{}.{}".format(
                                                                self.__info['media_id'],
                                                                i['page'],
                                                                file_ext_map[i['file_ext']]
                                                            )
                for i in self.__info['pages']]
    def download_task_render(self, path_: str):
        return [(
                    self.__id,
                    "https://i.nhentai.net/galleries/{}/{}.{}".format(
                            self.__info['media_id'],
                            i['page'],
                            file_ext_map[i['file_ext']]
                        ),
                    os.path.join(path_, str(self.__id), "{}.{}".format(i['page'], file_ext_map[i['file_ext']])),
                    self.__info['title']['japanese'],
                    i['page'],
                    self.__info['num_pages'],
                ) for i in self.__info['pages']]
    def live(self):
        return self.__alive