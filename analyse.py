import requests
import pandas as pd
import re
import json
import time
from requests import exceptions as RequestException
import math
import random
import os
from VARIABLES import *

# output_dir = ""

def get_fundcode():
    '''
    获取fundcode列表
    :return: 将获取的DataFrame以csv格式存入本地
    '''
    url = 'http://fund.eastmoney.com/js/fundcode_search.js'
    r = requests.get(url)
    cont = re.findall('var r = (.*])', r.text)[0]  # 提取list
    ls = json.loads(cont)  # 将字符串个事的list转化为list格式
    fundcode = pd.DataFrame(ls, columns=['fundcode', 'fundsx', 'name', 'category', 'fundpy'])  # list转为DataFrame
    fundcode = fundcode.loc[:, ['fundcode', 'name', 'category']]
    fundcode.to_csv(output_dir + '/fundcode.csv',encoding='utf-8-sig', index=False)


def check_path(path: str):
    if not os.path.exists(path):
        os.mkdir(path)


def get_one_page(fundcode, pageIndex=1):
    '''
    获取基金净值某一页的html
    :param fundcode: str格式，基金代码
    :param pageIndex: int格式，页码数
    :return: str格式，获取网页内容
    '''
    url = 'http://api.fund.eastmoney.com/f10/lsjz'
    cookie = 'EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; EMFUND8=null; EMFUND0=null; EMFUND9=01-24 17:11:50@#$%u957F%u4FE1%u5229%u5E7F%u6DF7%u5408A@%23%24519961; st_pvi=27838598767214; st_si=11887649835514'
    headers = {
        'Cookie': cookie,
        'Host': 'api.fund.eastmoney.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Referer': 'http://fundf10.eastmoney.com/jjjz_%s.html' % fundcode,
    }
    params = {
        'callback': 'jQuery18307633215694564663_1548321266367',
        'fundCode': fundcode,
        'pageIndex': pageIndex,
        'pageSize': 20,
    }
    try:
        r = requests.get(url=url, headers=headers, params=params)
        if r.status_code == 200:
            return r.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    '''
    解析网页内容
    :param html: str格式，html内容
    :return: dict格式，获取历史净值和访问页数
    '''
    if html is not None:  # 判断内容是否为None
        content = re.findall('\((.*?)\)', html)[0]  # 提取网页文本内容中的数据部分
        lsjz_list = json.loads(content)['Data']['LSJZList']  # 获取历史净值列表
        total_count = json.loads(content)['TotalCount']  # 获取数据量
        total_page = math.ceil(total_count / 20)  #
        lsjz = pd.DataFrame(lsjz_list)
        info = {'lsjz': lsjz,
                'total_page': total_page}
        return info
    return None


def main(fundcode):
    '''
    将爬取的基金净值数据储存至本地csv文件
    '''
    html = get_one_page(fundcode)
    info = parse_one_page(html)
    total_page = info['total_page']
    lsjz = info['lsjz']
    lsjz.to_csv(output_dir + '/%s_lsjz.csv' % fundcode, encoding="utf-8-sig", index=False)  # 将基金历史净值以csv格式储存
    page = 1
    while page < total_page:
        page += 1
        print(lsjz)
        html = get_one_page(fundcode, pageIndex=page)
        info = parse_one_page(html)
        if info is None:
            break
        lsjz = info['lsjz']
        lsjz.to_csv(output_dir + '/%s_lsjz.csv' % fundcode, encoding="utf-8-sig", mode='a', index=False, header=False)  # 追加存储
        time.sleep(random.randint(5, 10))


if __name__=='__main__':
    # 获取所有基金代码

    check_path(output_dir)
    get_fundcode()
    if full_funds_data:
        fundcodes = pd.read_csv(output_dir + '/fundcode.csv', converters={'fundcode': str}) ## This takes very long time
        fundcodes_looper = fundcodes['fundcode']
    else:
        fundcodes = [x.strip() for x in open('selectedFunds.txt', 'r', encoding= 'utf-8-sig').readlines()]
        fundcodes_looper = fundcodes
        # fundcode = '519961'
    # 获取所有基金净值数据
    for fundcode in fundcodes_looper:
        print(fundcode)
        main(fundcode)
        time.sleep(random.randint(5, 10))