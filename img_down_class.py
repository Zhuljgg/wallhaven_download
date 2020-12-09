"""
wallhaven
Toplist
"""
import os
import re
import requests


class Url_Data:
    def __init__(self):
        self.base_url = r'https://wallhaven.cc/'
        self.headers = {'User-Agent': 'Mozilla/5.0'}  # 使用浏览器UA
        # latest,hot,toplist,random
        self.option = {1: 'latest', 2: 'hot', 3: 'toplist', 4: 'random'}

    def get_real_url(self):
        choice = input('选择栏目: [1] Latest; [2] HOT; [3] TOPLIST; [4] RANDOM\n')
        return self.base_url + self.option[int(choice)]


class Wallhaven_Parser:
    def __init__(self, url_data, pic_down):
        self.real_url = url_data.get_real_url()
        self.headers = url_data.headers
        self.pic_down = pic_down

    def parse(self):
        num = self._input_num()
        for i in range(1, int(num) + 1):
            params = {'page': i}
            r = self._get_htmltext(params)
            self._parse_page(r)

    def _parse_page(self, r):
        # re 解析html
        wurl = r'https://wallhaven.cc/w/\w+? '
        src = re.findall(wurl, r.text)
        fulurl = r'https://w.wallhaven.cc/full/[A-Za-z0-9]{2}/wallhaven-\w+?(.jpg|.png)'
        count = 0
        if src:
            for each in src:
                print(each)
                r2 = requests.get(each, headers=self.headers, timeout=200)
                imgsrc = re.search(fulurl, r2.text)
                # print(imgsrc.group(0))
                filename = imgsrc.group(0)[-10:]
                print(filename)
                r = requests.get(imgsrc.group(0),
                                 headers=self.headers,
                                 timeout=200)
                if r.status_code == 200:
                    self.pic_down.show_tip()
                    self.pic_down.down_pic(r.content, filename)
                    count += 1
            print(f'共保存{count}张图片')
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

    def _get_htmltext(self, params):
        try:
            r = requests.get(self.real_url,
                             headers=self.headers,
                             params=params,
                             timeout=200)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r
        except BaseException as e:
            print(f'网页获取失败 {e}')


class Pic_Downloader:
    def __init__(self):
        self.filedir = r'wallhaven/'  # 文件保存目录

    def show_tip(self):
        # 提示
        tip = f'开始爬取\n' \
            f'当前图片保存目录为 {self.filedir}\n'\
            '-------------------------'
        print(tip)

    def down_pic(self, content, filename):
        filepath = self.filedir + filename
        try:
            if not os.path.exists(self.filedir):  # 如果文件保存目录不存在，新建
                os.makedirs(self.filedir)
            if not os.path.exists(filepath):  # 只有当文件不存在，才保存
                with open(filepath, 'wb') as f:
                    f.write(content)
                print(f'{filename} 保存成功')
        except BaseException as e:
            print(f'{filename} 保存失败 {e}')


if __name__ == "__main__":
    # url基础数据
    urldata = Url_Data()
    # 下载器，将来用协程改进
    pic_downloader = Pic_Downloader()
    # html解析器
    wallhaven_parser = Wallhaven_Parser(urldata, pic_downloader)
    # 移动网络延迟高，连接不上
    wallhaven_parser.parse()
