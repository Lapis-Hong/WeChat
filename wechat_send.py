#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lapis-hong
# @Date  : 2017/11/7
import os
import datetime as dt
import random
import sys
import logging

import itchat
from apscheduler.schedulers.background import BackgroundScheduler
import warnings

reload(sys)
sys.setdefaultencoding('utf-8')
logging.basicConfig()
warnings.filterwarnings("ignore")  # 忽略WARNING信息

NAME = 'Lapis-Hong'


def send():
    """发送消息函数"""
    meet_date = dt.date(2016, 5, 15)  # 跟某人相识日期
    today_date = dt.date.today()  # 今天日期
    pass_days = (today_date - meet_date).days  # 相识天数
    now = dt.datetime.now()  # 获取当前时间  datetime.datetime(2017, 11, 7, 15, 28, 23, 926233)
    now_time = now.strftime('%H:%M')  # 格式化时间，截取小时和分钟字段

    # send text
    content = ['Have you learned Python today?', 'best regards from Mr.H', 'Hello, little Jun',
               'Have you write the words?', 'Drink some water', 'Keep smiling', 'Do not look the phone',
               'Eat some thing', 'I miss U', 'How are you', 'Nice to meet you', 'Hi, little pig', 'Are you busy?'
               'Time to sleep', 'See you soon', 'Do not miss me', 'What are you doing?',
               ]  # 发送消息内容列表
    content_sample = random.choice(content)  # 随机选择消息列表中一条消息
    message = 'Today is our {} day, now it is {}. {}'.format(pass_days, now_time, content_sample)  # 发送的完整消息
    itchat.send(msg=message, toUserName=user_name)
    print('Already send the message: {}'.format(message))

    # send image
    image_dir = os.path.abspath('.') + '/image'  # 获取存储的图片路径 '/Users/lapis-hong/Documents/Python/untitled1/image'
    image_filenames = [f for f in os.listdir(image_dir) if f.endswith('.jpeg')]  # 获取图片路径下所有以.jpg结尾的文件名列表
    image_sample = random.choice(image_filenames)  # 随机选择一张图片
    image_path = os.path.join(image_dir, image_sample)
    itchat.send("@img@%s" % image_path, toUserName=user_name)  # 发送图片
    print('Already send a image: {}'.format(image_path))

    # 递归调用 my_scheduler
    next_time = now + dt.timedelta(minutes=30)  # 下一次发送消息时间, 输出 datetime.datetime(2017, 11, 7, 14, 21, 44, 269256)
    next_time = next_time.strftime('%Y-%m-%d %H:%M:%S')  # 格式化， 输出 '2017-11-07 14:21:44'
    my_scheduler(next_time)  # 启用下一次定时


def my_scheduler(run_time):
    """定时函数"""
    scheduler = BackgroundScheduler()  # 实例化
    scheduler.add_job(send, 'date', run_date=run_time)
    scheduler.start()


if __name__ == '__main__':
    # itchat.auto_login(enableCmdQR=False)  # True命令行二维码, 默认False是图片格式二维码
    itchat.auto_login(hotReload=True)  # 方便调试，不用每次都扫二维码
    # from friends name to get user id
    users_info = itchat.search_friends(name=NAME)
    print('User info: {}'.format(users_info))
    user_name = users_info[0]['UserName']  # User id @8935ca1e425e42432f5b7b8bb3f9244d1a9918ee954bdbafe8afc92a24dd1921
    print('User Name: {}'.format(user_name))

    send()  # 会递归调用send()
    itchat.run()  # 跑微信服务


