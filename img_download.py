"""
wallhaven
Toplist
"""
import os
import re
import requests


# 获取初始网页
def get_htmltext(url, headers, params):
    try:
        r = requests.get(url, headers=headers, params=params, timeout=200)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r
    except BaseException as e:
        print(f'网页获取失败 {e}')


# re 解析html
def parse_page(r, headers):
    wurl = r'https://wallhaven.cc/w/\w+'
    src = re.findall(wurl, r.text)
    fulurl = r'https://w.wallhaven.cc/full/[A-Za-z0-9]{2}/wallhaven-\w+?(.jpg|.png)'
    count = 0
    if src:
        for each in src:
            print(each)
            r2 = requests.get(each, headers=headers, timeout=200)
            imgsrc = re.search(fulurl, r2.text)
            # print(imgsrc.group(0))
            filename = imgsrc.group(0)[-10:]
            print(filename)
            r = requests.get(imgsrc.group(0), headers=headers, timeout=200)
            if r.status_code == 200:
                down_pic(r.content, filename)
                count += 1
        print(f'共保存{count}张图片')

    else:
        print('list is none')


# 解析页面，并执行文件操作
# def xpathparse_page(r, headers):
#     html = etree.HTML(r.text)
#     srcs = html.xpath(".//li//a[@class='preview']/@href")  # 获取到跳转页面

#     count = 0
#     for src in srcs:
#         r = requests.get(src, headers=headers, timeout=200)

#         html = etree.HTML(r.text)
#         img_src = html.xpath(".//img[@id='wallpaper']/@src")
#         # img_src 是只有一个元素的列表,所以直接可以下标取值
#         # print(img_src)
#         src = img_src[0]
#         fileName = src.split('/')[-1]  # 获取文件名
#         r = requests.get(src, headers=headers)  # full图
#         # 保存图片
#         down_pic(r.content, fileName)
#         # 计数+1
#         count += 1
#     print(f'当前保存 {count}张图片')


# 下载保存图片
def down_pic(content, filename):
    filepath = filedir + filename  # 完全路径

    try:
        if not os.path.exists(filedir):  # 如果文件保存目录不存在，新建
            os.makedirs(filedir)
        if not os.path.exists(filepath):  # 只有当文件不存在，才保存
            with open(filepath, 'wb') as f:
                f.write(content)
            print(f'{filename} 保存成功')
    except BaseException as e:
        print(f'{filename} 保存失败 {e}')


def input_num():
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


if __name__ == "__main__":
    filedir = r'wallhaven/'  # 文件保存目录
    headers = {'User-Agent': 'Mozilla/5.0'}  # 使用浏览器UA
    base_url = 'https://wallhaven.cc/toplist'
    # page = 1  # 爬取的页数，1

    # page = input_num()
    page = 1
    # 提示
    tip = f'开始爬取\n' \
        f'当前图片保存目录为 {filedir}\n'\
        '-------------------------'
    print(tip)

    # 主逻辑
    for i in range(1, page + 1):  # 爬取1页，1-2
        params = {"page": i}
        r = get_htmltext(base_url, headers, params)

        # 开始解析页面
        parse_page(r, headers)
