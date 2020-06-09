# -*- coding: utf-8 -*-
import random,requests,csv
from lxml import etree
from proxy_util import logger
from run import fifo_queue
from settings import USER_AGENT_LIST
from proxy_util import base_headers, request_page

# 测试地址
# url = 'http://blog.csdn.net/pengjunlee/article/details/90174453'
# url ='https://www.walmart.com/'
urlg = 'https://www.walmart.com{title}'
url = 'https://www.walmart.com/search/?grid=true&query={title1}'
# url = 'https://www.walmart.com/search/?grid=true&query=10pcs+Flower+Pot+Bottom+Square+Grid+Mat+Breathable+Drainage+Screens+Bottom+Hole+Mesh+Pad'


# 获取代理
proxy = fifo_queue.pop(schema='http')
proxies = {proxy.schema:proxy._get_url()}

# 构造请求头
headers = dict(base_headers)
if 'User-Agent' not in headers.keys():
    headers['User-Agent'] = random.choice(USER_AGENT_LIST)

response = None
successed = False
readlist = []
# html = ''
# category = ''
def req(url,titleList):
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=5)
        html = etree.HTML(response.content.decode('utf-8'))
        if (response.status_code == 200):
            successed = True
            # logger.info("使用代理< " + proxy._get_url() + " > 请求 < " + url + " > 结果： 成功 ")
    except:
        logger.info("使用代理< " + proxy._get_url() + " > 请求 < " + url + " > 结果： 失败 ")
        csv_filess = open('E:\\python\\环境1\\walmart\\Failure title.csv', 'a', newline='', encoding='utf-8')
        writerss = csv.writer(csv_filess)
        writerss.writerow([titleList])
        csv_filess.close()

    # 根据请求的响应结果更新代理
    proxy._update(successed)
    # 将代理返还给队列，返还时不校验可用性
    fifo_queue.push(proxy, need_check=False)
    return html

# 空格转换
def replaceSpace(s):
    item_list = []
    for c in s:
        if c == " ":
            item_list.append("+")
        else:
            item_list.append(c)
    return "".join(item_list)

# 读取需要爬取的标题
csv_read = open('E:\\python\\环境1\\walmart\\ip.csv', 'r', newline='', encoding='utf-8')
ree = csv.reader(csv_read)
for rei in ree:
    readlist.append(rei)
sr = len(readlist)

# 爬取后写入表格
csv_file = open('E:\\python\\环境1\\walmart\\wmt.csv', 'a', newline='', encoding='utf-8')
writers = csv.writer(csv_file)
for i in range(0,sr):
    try:
        titleList = readlist[i][0]
        vv = replaceSpace(titleList)
        urls = url.format(title1=vv)
        htmls = req(urls,titleList)
        list = htmls.xpath("//a[@class = 'product-title-link line-clamp line-clamp-2 truncate-title']/@href")
        urlq = urlg.format(title=list[0])
        category = req(urlq,titleList)
        categoryList = category.xpath("//ol[@class='breadcrumb-list']")
        for categoryLists in categoryList:
            categoryName = categoryLists.xpath("//li[@itemprop='itemListElement']/a/span/text()")
            ti = '>'.join(categoryName)
            writers.writerow([titleList, ti])
    except:
        pass
    continue

csv_read.close()
csv_file.close()
