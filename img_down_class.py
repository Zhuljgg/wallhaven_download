"""
wallhaven.cc
"""
import os
import re
import requests
import sys
import asyncio


# 工具类
class NetTool():
    @staticmethod
    def ping(url):
        # cmd调用ping命令
        s = 'www.' + re.search(r'https://(.+)/', url).group(1)
        os.system(f'ping {s}')


# URL数据类
class UrlData:
    def __init__(self):
        self.base_url = r'https://wallhaven.cc/'
        self.headers = {'User-Agent': 'Mozilla/5.0'}  # 使用浏览器UA
        # latest,hot,toplist,random
        self.option = {1: 'latest', 2: 'hot', 3: 'toplist', 4: 'random'}

    def get_real_url(self):
        # choice = input('选择栏目: [1] Latest; [2] HOT; [3] TOPLIST; [4] RANDOM\n')
        # 这里用4来测试
        return self.base_url + self.option[4]


# 解析网页类
class WallhavenParser:
    def __init__(self, url_data, pic_down, nettool):
        self.base_url = url_data.base_url
        self.real_url = url_data.get_real_url()
        self.headers = url_data.headers
        self.pic_down = pic_down
        self.net_tool = nettool

    def parse(self):
        print('- PING -')
        # ping 获取延迟
        self.net_tool.ping(self.base_url)
        print('- START -')
        num = self._input_num()
        for i in range(1, int(num) + 1):
            params = {'page': i}
            r = self._get_htmltext(self.real_url, params)
            self._parse_page(r)

    # div list,default n is 4
    @staticmethod
    def _div_list(l, n=4):
        """将一个列表分割成n个列表"""
        if n > 0:
            lists = [[] for _ in range(n)]
            i = 0
            for elem in l:
                lists[i].append(elem)
                i = (i + 1) % n
        return lists

    def _get_img(self):
        l = []
        count = 0
        uls = yield l
        # print(uls)
        for url in uls:
            r = self._get_htmltext(url)
            imgsrc = re.search(
                r'https://w.wallhaven.cc/full/[A-Za-z0-9]{2}/wallhaven-\w+(.jpg|.png)',
                r.text)
            r = self._get_htmltext(imgsrc.group(0))
            if r.status_code == 200:
                filename = imgsrc.group(0)[-10:]
                self.pic_down.down_img(r.content, filename)
                count += 1
            else:
                print(f'r.status_code : {r.status_code}')
                continue
        print(f'共保存{count}张图片')

    def _parse_page(self, r):
        # re 解析html
        wurl = r'https://wallhaven.cc/w/\w+'
        src = re.findall(wurl, r.text)
        if src:
            # 切割src
            src_lists = WallhavenParser._div_list(src)
            self.pic_down.show_tip()
            g = self._get_img()
            g.send(None)
            for each in src_lists:
                g.send(each)
            g.close()
        else:
            print('list is none')

    def _input_num(self):
        while True:
            page = input('请输入想要爬取的网页页数：')
            try:
                num = eval(page)
                if isinstance(num, int):  # 判断是否为int
                    if num <= 0:
                        print('请输入大于0的数')
                        continue
                    else:
                        return num
                else:
                    print('请输入整数')
            except BaseException as e:
                print(f'异常 {e}')

    def _get_htmltext(self, url, params=None):
        try:
            r = requests.get(url,
                             headers=self.headers,
                             params=params,
                             timeout=30)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r
        except BaseException as e:
            print(f'网页获取失败 {e}')


# 图片下载类
class ImgDownloader:
    def __init__(self):
        self.filedir = r'wallhaven/'  # 文件保存目录

    def show_tip(self):
        # 提示
        tip = f'开始爬取\n' \
            f'当前图片保存目录为 {self.filedir}\n'\
            '-------------------------'
        print(tip)

    def down_img(self, content, filename):
        filepath = self.filedir + filename
        try:
            if not os.path.exists(self.filedir):  # 如果文件保存目录不存在，则新建
                os.makedirs(self.filedir)
            if not os.path.exists(filepath):  # 只有当文件不存在，才保存
                with open(filepath, 'wb') as f:
                    f.write(content)
                print(f'{filename} 保存成功')
        except BaseException as e:
            print(f'{filename} 保存失败 {e}')


if __name__ == "__main__":
    # url基础数据
    url_data = UrlData()
    # 下载器，将来用协程改进
    img_downloader = ImgDownloader()
    # html解析器
    wallhaven_parser = WallhavenParser(url_data, img_downloader, NetTool)
    # 移动网络延迟高
    wallhaven_parser.parse()
