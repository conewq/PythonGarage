#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: conewq 
# Purpose: 
# Version: 
# Date: 2019-04-29 17:05:52 
# Last Modified by: conewq 
# Last Modified time: 2019-04-29 17:05:52 

import re
import bs4
import time
import sqlite3
import urllib
import urllib.request
import string
import os
import os.path
import sys
import random
import traceback
from wy_send_mail import wy_mail_sender


def html_generator(html_eles):
    html_content = "<html>\n<head>\n<meta charset=\"utf-8\">\n</head>\n<body>\n"
    html_tail = "</body>\n</html>"

    html_num = 1
    for html_com in html_eles:
        html_info = "<p>\n"
        html_info += "<p><b>Commodity No.%s:</b></p>\n" % (str(html_num))
        html_info += "<p>%s</p>\n" % (html_com[2])
        html_info += "<p>%s</p>\n" % (html_com[-1])
        html_info += "<a href=\"%s\">%s</a><br>\n" % (html_com[0],html_com[1])
        html_info += "<p>%s</p>\n" % (html_com[3])
        html_info += "<img src=\"%s\"/>\n" % (html_com[4])
        html_info += "</p>\n"
        html_content += html_info
        html_num += 1
    
    html_content += html_tail
    return html_content


def main():
    current_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    os.chdir(os.path.split(os.path.realpath(__file__))[0])
    try:
        com_conn = sqlite3.connect('smzdm_commodity.db')
    except:
        print('数据库连接失败，请检查数据库文件。')
        sys.exit()

    self_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3314.0 Safari/537.36 SE 2.X MetaSr 1.0'
    }

    #监控的关键词
    keywords = [
        'superstar',
        'onitsuka+mexico+66',
        'asics+男',
        '希捷+酷狼+4t',
        '罗技+anywhere',
        '保友金豪b'
        ]
    
    # 发邮件通知的关键词
    mail_keywords = [
        'superstar',
        # 'onitsuka+mexico+66',
        # 'asics+男',
        '希捷+酷狼+4t'
        # '罗技+anywhere',
        # '保友金豪b'
        ]
    
    page_num = 1  #设置翻页数

    coms_mail = []
    for kword in keywords:
        cur_com = com_conn.execute("select com_id from commodities;")
        cur_coms = [i[0] for i in cur_com.fetchall()]
        for page_id in range(1, page_num + 1):
            url = urllib.parse.quote("https://search.smzdm.com/?c=faxian&s=%s&order=time&v=b&p=%s" %  \
                (kword,str(page_id)),safe = string.printable)  #处理url中含有中文的问题
            req = urllib.request.Request(url,headers = self_headers)
            print("正在查询关键词：%s。第%s页..." % (kword,str(page_id)))
            html = urllib.request.urlopen(req)
            page = html.read().decode("utf8")
            soup = bs4.BeautifulSoup(page, 'lxml')
            try:
                comBlock = soup.find_all('ul', id='feed-main-list')[0]
            except:
                print("本页数据解析错误，跳转至下一页...")
                continue
            com_list = comBlock.find_all('div', class_='feed-block z-hor-feed')
            for com in com_list:
                com_info = [kword]
                com_mail = []
                try:
                    com_link = com.find_all('a')[0]['href']
                    com_id = re.search('\d+',com_link).group()
                    if int(com_id) in cur_coms:
                        continue
                    else:
                        com_img = com.find_all('img')[0]
                        com_imglink = 'https:' + com_img['src']
                        com_title = com_img['alt']
                        com_priceinfo = com.find_all('div',class_='z-highlight')[0].text.strip()
                        try:
                            com_price = re.match('\d+(\.\d+)?',com_priceinfo).group()
                        except:
                            com_price = ''
                        try:
                            com_description = com.find_all('div',class_='feed-block-descripe-top')[0].text.strip()
                        except:
                            com_description = ''
                        com_timeinfo = com.find_all('span')[-2].text.strip()
                        try:
                            com_time = re.search('\d+:\d+',com_timeinfo).group() + ':00'
                        except:
                            com_time = ''
                        if com_time == '':
                            com_onlinetime = re.search('\d+-\d+-\d+',com_timeinfo).group()
                        else:
                            try:
                                com_date = time.strftime("%Y-",time.localtime()) + re.search('\d+-\d+',com_timeinfo).group()
                            except:
                                com_date = time.strftime("%Y-%m-%d",time.localtime())
                            com_onlinetime = com_date + ' ' + com_time
                        com_source = com.find_all('span')[-1].text.strip()

                        if kword in mail_keywords:
                            com_mail.append(com_link)
                            com_mail.append(com_title)
                            com_mail.append(com_priceinfo)
                            com_mail.append(com_description)
                            com_mail.append(com_imglink)
                            com_mail.append(com_source)
                            coms_mail.append(com_mail)

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
                        com_conn.execute("insert into commodities ('keyword','com_id','com_title','com_price','com_priceinfo', \
                                        'com_description','com_source','com_detailurl','com_img','com_onlinetime') values (?,?,?,?,?,?,?,?,?,?);" , \
                                        (com_info[0],com_info[1],com_info[2],com_info[3],com_info[4],com_info[5],com_info[6],com_info[7],com_info[8],com_info[9]))
                except:
                    print(traceback.format_exc())
                    print("报错信息：\n关键词：%s\n页数：%s\n商品ID：%s" % (kword,str(page_id),com_id))
                    continue

            com_conn.commit()
    com_conn.close()

    if len(coms_mail) != 0:
        update_content = html_generator(coms_mail)
        wy_mail_sender("News from SMZDM %s" % (current_time),update_content)
        

if __name__=='__main__':
    main()
