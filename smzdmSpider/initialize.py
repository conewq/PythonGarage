#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: conewq
# Purpose: 
# Usage: 
# Version: 
# Created: 2019-10-21 15:21:24

import sqlite3
import os
import bs4
import urllib.request
import re
import time
import random

def main():
    os.chdir('D:/PythonGarage/smzdmSpider')
    com_conn = sqlite3.connect('smzdm_commodity.db')
    com_conn.execute("""
        create table if not exists commodities(
            id INTEGER PRIMARY KEY autoincrement,
            keyword nvarchar(255),
            com_id int not null,
            com_title nvarchar(255),
            com_price real,
            com_priceinfo nvarchar(255),
            com_description nvarchar(255),
            com_source nvarchar(255),
            com_detailurl nvarchar(255),
            com_img nvarchar(255),
            com_onlinetime datetime,
            CreateTime timestamp not null default (datetime('now','localtime'))
        )
    """)    

    self_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3314.0 Safari/537.36 SE 2.X MetaSr 1.0'
    }
    keywords = [
        'superstar',
        'onitsuka+mexico+66',
        'asics'
        ]
    for kword in keywords:
        for page_id in range(1,11):
            req = urllib.request.Request("https://search.smzdm.com/?c=faxian&s=%s&order=time&v=b&p=%s" % (kword,str(page_id)),headers = self_headers)
            print("正在采集关键词：%s。第%s页..." % (kword,str(page_id)))
            html = urllib.request.urlopen(req)
            page = html.read().decode("utf8")
            soup = bs4.BeautifulSoup(page, 'lxml')
            comBlock = soup.find_all('ul', id='feed-main-list')[0]
            com_list = comBlock.find_all('div', class_='feed-block z-hor-feed')
            for com in com_list:
                com_info = [kword]
                try:
                    com_link = com.find_all('a')[0]['href']
                    com_id = re.search('\d+',com_link).group()
                    com_img = com.find_all('img')[0]
                    com_imglink = 'https:' + com_img['src']
                    com_title = com_img['alt']
                    com_priceinfo = com.find_all('div',class_='z-highlight')[0].text.strip()
                    try:
                        com_price = re.match('\d+(\.\d+)?',com_priceinfo).group()
                    except:
                        com_price = ''
                    com_description = com.find_all('div',class_='feed-block-descripe')[0].text.strip()
                    com_timeinfo = com.find_all('span')[-2].text.strip()
                    com_time = re.search('\d+:\d+',com_timeinfo).group()
                    try:
                        com_date = time.strftime("%Y-",time.localtime()) + re.search('\d+-\d+',com_timeinfo).group()
                    except:
                        com_date = time.strftime("%Y-%m-%d",time.localtime())
                    com_onlinetime = com_date + ' ' + com_time + ':00'
                    com_source = com.find_all('span')[-1].text.strip()
                except:
                    print("报错信息：\n关键词：%s\n页数：%s\n商品ID：%s" % (kword,str(page_id),com_id))
                    continue
                
                com_info.append(com_id)
                com_info.append(com_title)
                com_info.append(com_price)
                com_info.append(com_priceinfo)
                com_info.append(com_description)
                com_info.append(com_source)
                com_info.append(com_link)
                com_info.append(com_imglink)
                com_info.append(com_onlinetime)
                
                print('\n'.join(com_info))
                time.sleep(1)
                com_conn.execute("insert into commodities ('keyword','com_id','com_title','com_price','com_priceinfo', \
                'com_description','com_source','com_detailurl','com_img','com_onlinetime') values (?,?,?,?,?,?,?,?,?,?);" , \
                (com_info[0],com_info[1],com_info[2],com_info[3],com_info[4],com_info[5],com_info[6],com_info[7],com_info[8],com_info[9]))
            time.sleep(random.randint(5,10))
            com_conn.commit()
    com_conn.close()

if __name__ == '__main__':
    main()