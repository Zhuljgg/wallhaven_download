"""
wallhaven.cc
"""
import requests
import re
import os
import time
import asyncio
import aiohttp


class WallhavenSpider():
    def __init__(self, tool):
        self.headers = {'User-Agent': 'Mozilla/5.0'}  # 使用浏览器UA
        self.base_url = r'https://wallhaven.cc/'
        # latest,hot,toplist,random
        self.option = {1: 'latest', 2: 'hot', 3: 'toplist', 4: 'random'}
        self.tool = tool
        self.filedir = r'wallhaven/'
        self.count = 1

    def get_whole_url(self):
        # choice = input('选择栏目: [1] Latest; [2] HOT; [3] TOPLIST; [4] RANDOM\n')
        # 这里用3来测试
        return self.base_url + self.option[3]

    def run(self):
        print('- START -')
        self.tool.show_tip(self.filedir)
        start = time.time()
        self._parse()
        end = time.time()
        print(f'共运行了{end-start}秒')

    async def main(self, links):
        # tasks
        tasks = [(self._down_img(wlink))
                 for wlink in links]
        await asyncio.gather(*tasks)

    def _parse(self):
        # num = self.tool.get_input()
        wlist = []
        for i in range(1, 1 + 1):
            params = {'page': i}
            wlist.extend(self._get_w_links(params))
        links = wlist[:3]
        print(links)
        # # tasks
        # tasks = [(self._down_img(wlink))
        #          for wlink in links]
        asyncio.run(self.main(links))
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(asyncio.wait(tasks))
        # loop.run_until_complete(asyncio.gather(tasks))
        # loop.close()

    # 获取html的内容
    def _get_htmltext(self, url, params=None):
        try:
            r = requests.get(url,
                             headers=self.headers,
                             params=params,
                             timeout=30)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            if r.status_code == 200:
                return r
        except BaseException as e:
            print(f'网页获取失败 {e} {r.status_code}')
        # except:
        #     print(f'UnknownError: {e}')

    async def _get_html_content(self, link):
        async with aiohttp.ClientSession() as session:
            resp = await session.get(link)
            content = await resp.read()
            return content

    def _get_w_links(self, params):
        r = self._get_htmltext(self.get_whole_url(), params)
        patt = r'https://wallhaven.cc/w/\w+'
        links = re.findall(patt, r.text)
        if links:
            return links
        else:
            print('links is none')

    # 下载到文件
    async def _down_img(self, link):
        # link 是w url，需要再get full url
        r = self._get_htmltext(link)
        # r = await self._get_html_content(link)
        # print(r)
        imgsrc = re.search(
            r'https://w.wallhaven.cc/full/[A-Za-z0-9]{2}/wallhaven-\w+(.jpg|.png)',
            r.text)
        # print(imgsrc)
        # print(imgsrc.group(0))
        content = await self._get_html_content(imgsrc.group(0))
        filename = imgsrc.group(0)[-10:]
        filepath = self.filedir + filename
        try:
            if not os.path.exists(self.filedir):  # 如果文件保存目录不存在，则新建
                os.makedirs(self.filedir)
            if not os.path.exists(filepath):  # 只有当文件不存在，才保存
                with open(filepath, 'wb') as f:
                    f.write(content)
                print(f'第{self.count}张图片 {filename} 保存成功')
                self.count += 1
        except BaseException as e:
            print(f'{filename} 保存失败 {e}')


# 工具类
class SpiderTool():
    @ staticmethod
    def ping(url):
        # cmd调用ping命令
        s = 'www.' + re.search(r'https://(.+)/', url).group(1)
        print('- PING -')
        os.system(f'ping {s}')

    @ staticmethod
    def get_input():
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

    # div list,default n is 4
    @ staticmethod
    def div_list(l, n=4):
        """将一个列表分割成n个列表"""
        if n > 0:
            lists = [[] for _ in range(n)]
            i = 0
            for elem in l:
                lists[i].append(elem)
                i = (i + 1) % n
        return lists

    @ staticmethod
    def show_tip(filedir):
        # 提示
        tip = f'开始爬取\n' \
            f'当前图片保存目录为 {filedir}\n'\
            '------------------------------------'
        print(tip)


if __name__ == "__main__":
    spider = WallhavenSpider(SpiderTool)
    # spider.tool.ping(spider.base_url)
    spider.run()
