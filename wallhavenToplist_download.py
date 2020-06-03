import requests
from lxml import etree
import os


# 获取初始网页
def getHTMLText(url, headers, params):
    try:
        r = requests.get(url, headers=headers, params=params, timeout=200)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r
    except BaseException as e:
        print(f'网页获取失败 {e}')
        return ''


# 解析页面，并执行文件操作
def parsePage(r, headers):
    html = etree.HTML(r.text)
    srcs = html.xpath(".//li//a[@class='preview']/@href")  # 获取到跳转页面

    count = 0
    for src in srcs:
        r = requests.get(src, headers=headers, timeout=200)

        html = etree.HTML(r.text)
        img_src = html.xpath(".//img[@id='wallpaper']/@src")
        # img_src 是只有一个元素的列表,所以直接可以下标取值
        # print(img_src)
        src = img_src[0]
        fileName = src.split('/')[-1]  # 获取文件名
        r = requests.get(src, headers=headers)  # full图
        # 保存图片
        downPic(r.content, fileName)
        # 计数+1
        count += 1
    print(f'当前保存 {count}张图片')

    # for src in img_src:
    #     fileName = src.split('/')[-1]  # 获取文件名
    #     r = requests.get(src, headers=headers)  # full图
    #
    #     # 保存图片
    #     downPic(r.content, fileName)
    #     # 计数+1
    #     count += 1


# 下载保存图片
def downPic(content, filename):
    # fileBasePath = "D://爬取内容//wallhaven//"  # 文件保存目录
    filePath = fileBasePath + filename  # 完全路径

    try:
        if not os.path.exists(fileBasePath):  # 如果文件保存目录不存在，新建
            os.makedirs(fileBasePath)
        if not os.path.exists(filePath):  # 只有当文件不存在，才保存
            with open(filePath, 'wb') as f:
                f.write(content)
            print(f'{filename} 保存成功')
    except BaseException as e:
        print(f'{filename} 保存失败 {e}')


def getInputInt():
    while True:
        page = input('请输入想要爬取的网页页数：')
        try:
            inputPage = eval(page)
            if isinstance(inputPage, int):  # 判断是否为int
                if inputPage <= 0:
                    print('请输入大于0的数')
                    continue
                else:
                    return inputPage
            else:
                print('请输入整数')
        except BaseException as e:
            print(f'异常 {e}')


if __name__ == "__main__":
    fileBasePath = "D://爬取内容//wallhaven//"  # 文件保存目录
    headers = {'User-Agent': 'Mozilla/5.0'}  # 使用浏览器UA
    base_url = 'https://wallhaven.cc/toplist'
    # page = 1  # 爬取的页数，1

    page = getInputInt()
    # 提示
    tip = f'开始爬取\n' \
        f'当前图片保存目录为 {fileBasePath}\n'\
        '-------------------------'
    print(tip)
    # print('开始爬取')
    # print(f'当前图片保存目录为 {fileBasePath}')
    # print()

    # 主逻辑
    for i in range(1, page + 1):  # 爬取1页，1-2
        params = {"page": i}
        r = getHTMLText(base_url, headers, params)

        # 开始解析页面
        parsePage(r, headers)
