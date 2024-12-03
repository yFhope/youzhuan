'''
郴州文旅爬虫
-  郴州要览 板块
-  增量爬虫 - 每天执行一次 抓取当天内容
-  只抓发文数量，不抓详情内容

'''

import time
import functools

import requests
from lxml import etree

# 列表页url
# index_url = 'http://www.app.czs.gov.cn/lywsj/zwgk/lydt/default.jsp?pager.offset=0&pager.desc=false'

# headers
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

# 用于错误自动重试
def retry(max_retries=3, delay=1):
    """
    错误重试装饰器
    :param max_retries: 最大重试次数
    :param delay: 每次重试前的延迟时间（秒）
    :return: 装饰器函数
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"尝试 {attempt} 失败: {e}， {delay} 秒后重试...")   # Retrying in 3 seconds
                    time.sleep(delay)
            # 如果最大重试次数用完后依然抛出异常，则抛出最后捕获的异常
            print(f"All {max_retries} attempts failed.")
            raise last_exception
        return wrapper
    return decorator

@retry(max_retries=3, delay=3)
def get_response(url):
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    if response.status_code == 200:
        return response
    raise Exception(f"get_response - url请求失败，状态码: {response.status_code}")

def parse_list_page(url):
    response = get_response(url)
    doc = etree.HTML(response.text)
    # 每篇新闻的发布时间
    release_time = doc.xpath('//*[@class="fz-tab"]/table/tbody/tr/td[3]/text()')
    # 获取当前页所有新闻的详情页url  - 用于后续计数
    hrefs = doc.xpath('//*[@class="fz-tab"]/table/tbody/tr//a/@href')
    item = {}
    item['hrefs'] = hrefs
    item['release_time'] = release_time
    item['count'] = len(hrefs)
    return item

def save_data(data):
    pass

def main():
    # 定时任务，每一小时执行一次，只抓取增量数据，只抓第一页
    index_url = f'http://www.app.czs.gov.cn/lywsj/zwgk/lydt/default.jsp?pager.offset=0&pager.desc=false'
    item = parse_list_page(index_url)
    count = item['count']
    print("当前页数据:")
    print(item['release_time'])
    print(item['hrefs'])



if __name__ == '__main__':
    main()

