#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lapis-hong
# @Date  : 2017/11/7
import sys
import time
import random
import itchat
import requests

reload(sys)
sys.setdefaultencoding('utf-8')


def get_response(msg):
    url = 'http://www.tuling123.com/openapi/api'
    data = {'key': '75137612d89c42f0b9d7a3f5133ec656',
            'info': msg,
            'userid': 'pth-robot'}
    try:
        r = requests.post(url, data=data).json()
        return r.get('text')
    except:
        return  # 返回None


@itchat.msg_register(itchat.content.TEXT, isFriendChat=True, isGroupChat=False, isMpChat=False)
def tuling_reply(msg):
    if msg['FromUserName'] in user_list:
        time.sleep(random.random() * 2)
        reply = get_response(msg['Text'])
        print(msg)
        del msg
        # a or b的意思是，如果a有内容，那么返回a，否则返回b， 为了保证在图灵Key出现问题的时候仍旧可以回复，这里设置一个默认回复
        return reply or 'I received: ' + msg.get('Text')


# @itchat.msg_register(itchat.content.TEXT)
# def text_reply(msg):  # msg is a dict
#     if msg['FromUserName'] == user_name:  # 自动回复某人信息
#         return '爸爸正忙，请稍后在拨，爸爸不在，好好学习，爸爸回家要监督你，嘻嘻嘻'


if __name__ == '__main__':
    itchat.auto_login(hotReload=True)
    name_list = ['Lapis-Hong']
    user_list = [itchat.search_friends(name=name)[0]['UserName'] for name in name_list]
    itchat.run()
