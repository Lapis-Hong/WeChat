#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lapis-hong
# @Date  : 2017/11/7
import bs4
import urllib
import sys
import datetime as dt
import logging

import itchat
from apscheduler.schedulers.background import BackgroundScheduler

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig()


def get_weather():
    wheatherHtml = urllib.urlopen('http://www.weather.com.cn/weather/101010100.shtml').read().decode('utf8')
    webpage = bs4.BeautifulSoup(wheatherHtml)
    body = webpage.body
    data = body.find('div', {'id': '7d'})
    ul = data.find('ul')
    li = ul.find_all('li')
    final = []
    for day in li:  # 对每个li标签中的内容进行遍历
        temp = []
        date = day.find('h1').string  # 找到日期
        temp.append(date)
        inf = day.find_all('p')  # 找到所有p标签
        temp.append(inf[0].string)  # 将天气状况加到temp中
        if inf[1].find('span') is None:
            temperature_highest = None
        else:
            temperature_highest = inf[1].find('span').string
            # temperature_highest = temperature_highest.replace('℃', '')  # 到了晚上网站会变，最高温度后面也有个℃
        temperature_lowest = inf[1].find('i').string  # 找到最低温
        # temperature_lowest = temperature_lowest.replace('℃', '')
        temp.append(temperature_highest)  # 将最高温添加到temp中
        temp.append(temperature_lowest)  # 将最低温添加到temp中
        final.append(temp)
    if int(final[1][3].replace('℃', '')) <= -10:
        word = '<明天非常非常非常冷，宝宝穿上所有能穿的！>'
    elif -10 < int(final[1][3].replace('℃', '')) <= -5:
        word = '<明天很冷很冷很冷，宝宝多穿多穿多穿！>'
    elif -5 < int(final[1][3].replace('℃', '')) <= 0:
        word = '<明天小冷，宝宝多穿点哦~>'
    else:
        word = '<明天不太冷，宝宝随意穿~>'
    tom = final[1]
    tom[2] = '最高气温:' + tom[2]
    tom[3] = '最低气温:' + tom[3]
    return ' '.join(tom) + '  ' + word


def send():
    itchat.send(msg=content, toUserName=user_name)
    now = dt.datetime.now()
    next_time = now + dt.timedelta(days=1)  # 下一次发送消息时间, 输出 datetime.datetime(2017, 11, 7, 14, 21, 44, 269256)
    next_time = next_time.strftime('%Y-%m-%d %23:%30:%00')  # 明天的23：30再次发送消息
    my_scheduler(next_time)  # 启用下一次定时


def my_scheduler(run_time):
    """定时函数"""
    scheduler = BackgroundScheduler()  # 实例化
    scheduler.add_job(send, 'date', run_date=run_time)
    scheduler.start()


if __name__ == '__main__':
    itchat.auto_login(hotReload=True)  # 方便调试，不用每次都扫二维码
    users_info = itchat.search_friends(name='某某某')
    user_name = users_info[0]['UserName']  # User id @8935ca1e425e42432f5b7b8bb3f9244d1a9918ee954bdbafe8afc92a24dd1921
    content = get_weather()
    send()
    itchat.run()


