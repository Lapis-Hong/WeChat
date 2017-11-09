#!/usr/bin/env python
# coding=utf-8
"""# wechat-deleted-friends
查看被删的微信好友
原理就是新建群组,如果加不进来就是被删好友了(不要在群组里讲话,别人是看不见的)
用的是微信网页版的接口 查询结果可能会引起一些心理上的不适,请小心使用..(逃
还有些小问题: 结果好像有疏漏一小部分,原因不明.. 最终会遗留下一个只有自己的群组,需要手工删一下
没试过被拉黑的情况
用法：
`$ python wdf.py`
按指示做即可"""
from __future__ import print_function

import os
import re
import time
import xml.dom.minidom
import json
import sys
import math
import subprocess
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

try:
    import urllib2 as wdf_urllib
    from cookielib import CookieJar
except ImportError:
    import urllib.request as wdf_urllib
    from http.cookiejar import CookieJar

try:
    range = xrange
except:
    pass

DEBUG = False

MAX_GROUP_NUM = 35  # 每组人数

QRImagePath = os.path.join(os.getcwd(), 'qrcode.jpg')

tip = 0
uuid = ''

base_uri = ''
redirect_uri = ''

skey = ''
wxsid = ''
wxuin = ''
pass_ticket = ''
deviceId = 'e000000000000000'

BaseRequest = {}

ContactList = []
My = []


def get_request(url, data=None):
    try:
        data = data.encode('utf-8')
    except:
        pass
    finally:
        return wdf_urllib.Request(url=url, data=data)


def get_uuid():
    global uuid
    url = 'https://login.weixin.qq.com/jslogin'
    params = {
        'appid': 'wx782c26e4c19acffb',
        'fun': 'new',
        'lang': 'zh_CN',
        '_': int(time.time()),
    }
    request = get_request(url=url, data=urlencode(params))
    response = wdf_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')
    # print(data)
    # window.QRLogin.code = 200; window.QRLogin.uuid = "oZwt_bFfRg==";
    regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
    pm = re.search(regx, data)
    code = pm.group(1)
    uuid = pm.group(2)
    if code == '200':
        return True
    return False


def showQRImage():
    global tip

    url = 'https://login.weixin.qq.com/qrcode/' + uuid
    params = {
        't': 'webwx',
        '_': int(time.time()),
    }

    request = get_request(url = url, data = urlencode(params))
    response = wdf_urllib.urlopen(request)

    tip = 1

    f = open(QRImagePath, 'wb')
    f.write(response.read())
    f.close()

    if sys.platform.find('darwin') >= 0:
        subprocess.call(['open', QRImagePath])
    elif sys.platform.find('linux') >= 0:
        subprocess.call(['xdg-open', QRImagePath])
    else:
        os.startfile(QRImagePath)

    print('请使用微信扫描二维码以登录')

def waitForLogin():
    global tip, base_uri, redirect_uri

    url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (tip, uuid, int(time.time()))

    request = get_request(url = url)
    response = wdf_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')

    # print(data)

    # window.code=500;
    regx = r'window.code=(\d+);'
    pm = re.search(regx, data)

    code = pm.group(1)

    if code == '201': #已扫描
        print('成功扫描,请在手机上点击确认以登录')
        tip = 0
    elif code == '200': #已登录
        print('正在登录...')
        regx = r'window.redirect_uri="(\S+?)";'
        pm = re.search(regx, data)
        redirect_uri = pm.group(1) + '&fun=new'
        base_uri = redirect_uri[:redirect_uri.rfind('/')]
    elif code == '408': #超时
        pass
    # elif code == '400' or code == '500':

    return code


def login():
    global skey, wxsid, wxuin, pass_ticket, BaseRequest
    request = get_request(url = redirect_uri)
    response = wdf_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')
    # print(data)
    '''
        <error>
            <ret>0</ret>
            <message>OK</message>
            <skey>xxx</skey>
            <wxsid>xxx</wxsid>
            <wxuin>xxx</wxuin>
            <pass_ticket>xxx</pass_ticket>
            <isgrayscale>1</isgrayscale>
        </error>
    '''
    doc = xml.dom.minidom.parseString(data)
    root = doc.documentElement
    for node in root.childNodes:
        if node.nodeName == 'skey':
            skey = node.childNodes[0].data
        elif node.nodeName == 'wxsid':
            wxsid = node.childNodes[0].data
        elif node.nodeName == 'wxuin':
            wxuin = node.childNodes[0].data
        elif node.nodeName == 'pass_ticket':
            pass_ticket = node.childNodes[0].data
    # print('skey: %s, wxsid: %s, wxuin: %s, pass_ticket: %s' % (skey, wxsid, wxuin, pass_ticket))
    #if skey == '' or wxsid == '' or wxuin == '' or pass_ticket == '':
        #return False
    if not all((skey, wxsid, wxuin, pass_ticket)):
        return False
    BaseRequest = {
        'Uin': int(wxuin),
        'Sid': wxsid,
        'Skey': skey,
        'DeviceID': deviceId,
    }
    return True


def webwxinit():
    url = base_uri + '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (pass_ticket, skey, int(time.time()))
    params = {
        'BaseRequest': BaseRequest
    }

    request = get_request(url = url, data = json.dumps(params))
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    response = wdf_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')
    if DEBUG:
        #f = open(os.getcwd() + '/webwxinit.json', 'wb')
        f = open(os.path.join(os.getcwd(), 'webwxinit.json'), 'wb')
        f.write(data)
        f.close()
    global ContactList, My
    dic = json.loads(data)
    ContactList = dic['ContactList']
    My = dic['User']

    ErrMsg = dic['BaseResponse']['ErrMsg']
    if len(ErrMsg) > 0:
        print(ErrMsg)
    Ret = dic['BaseResponse']['Ret']
    if Ret != 0:
        return False
    return True


def webwxgetcontact():
    url = base_uri + '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (pass_ticket, skey, int(time.time()))
    request = get_request(url = url)
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    response = wdf_urllib.urlopen(request)
    data = response.read()
    if DEBUG:
        # f = open(os.getcwd() + '/webwxgetcontact.json', 'wb')
        f = open(os.path.join(os.getcwd(), 'webwxgetcontact.json'), 'wb')
        f.write(data)
        f.close()
    # print(data)
    data = data.decode('utf-8','replace')
    dic = json.loads(data)
    MemberList = dic['MemberList']
    # 倒序遍历,不然删除的时候出问题..
    SpecialUsers = ['newsapp', 'fmessage', 'filehelper', 'weibo', 'qqmail', 'fmessage', 'tmessage', 'qmessage', 'qqsync', 'floatbottle', 'lbsapp', 'shakeapp', 'medianote', 'qqfriend', 'readerapp', 'blogapp', 'facebookapp', 'masssendapp', 'meishiapp', 'feedsapp', 'voip', 'blogappweixin', 'weixin', 'brandsessionholder', 'weixinreminder', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'officialaccounts', 'notification_messages', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'wxitil', 'userexperience_alarm', 'notification_messages']
    for i in range(len(MemberList) - 1, -1, -1):
        Member = MemberList[i]
        if Member['VerifyFlag'] & 8 != 0: # 公众号/服务号
            MemberList.remove(Member)
        elif Member['UserName'] in SpecialUsers: # 特殊账号
            MemberList.remove(Member)
        elif Member['UserName'].find('@@') != -1: # 群聊
            MemberList.remove(Member)
        elif Member['UserName'] == My['UserName']: # 自己
            MemberList.remove(Member)
    return MemberList


def createChatroom(UserNames):
    #MemberList = []
    #for UserName in UserNames:
        #MemberList.append({'UserName': UserName})
    MemberList = [{'UserName': UserName} for UserName in UserNames]
    url = base_uri + '/webwxcreatechatroom?pass_ticket=%s&r=%s' % (pass_ticket, int(time.time()))
    params = {
        'BaseRequest': BaseRequest,
        'MemberCount': len(MemberList),
        'MemberList': MemberList,
        'Topic': '',
    }
    request = get_request(url = url, data = json.dumps(params))
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    response = wdf_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')
    # print(data)
    dic = json.loads(data)
    ChatRoomName = dic['ChatRoomName']
    MemberList = dic['MemberList']
    DeletedList = []
    for Member in MemberList:
        if Member['MemberStatus'] == 4: #被对方删除了
            DeletedList.append(Member['UserName'])
    ErrMsg = dic['BaseResponse']['ErrMsg']
    if len(ErrMsg) > 0:
        print(ErrMsg)
    return ChatRoomName, DeletedList


def deleteMember(ChatRoomName, UserNames):
    url = base_uri + '/webwxupdatechatroom?fun=delmember&pass_ticket=%s' % (pass_ticket)
    params = {
        'BaseRequest': BaseRequest,
        'ChatRoomName': ChatRoomName,
        'DelMemberList': ','.join(UserNames),
    }
    request = get_request(url = url, data = json.dumps(params))
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    response = wdf_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')
    # print(data)
    dic = json.loads(data)
    ErrMsg = dic['BaseResponse']['ErrMsg']
    if len(ErrMsg) > 0:
        print(ErrMsg)
    Ret = dic['BaseResponse']['Ret']
    if Ret != 0:
        return False
    return True


def addMember(ChatRoomName, UserNames):
    url = base_uri + '/webwxupdatechatroom?fun=addmember&pass_ticket=%s' % (pass_ticket)
    params = {
        'BaseRequest': BaseRequest,
        'ChatRoomName': ChatRoomName,
        'AddMemberList': ','.join(UserNames),
    }
    request = get_request(url = url, data = json.dumps(params))
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    response = wdf_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')
    # print(data)
    dic = json.loads(data)
    MemberList = dic['MemberList']
    DeletedList = []
    for Member in MemberList:
        if Member['MemberStatus'] == 4: #被对方删除了
            DeletedList.append(Member['UserName'])
    ErrMsg = dic['BaseResponse']['ErrMsg']
    if len(ErrMsg) > 0:
        print(ErrMsg)
    return DeletedList

def main():
    try:
        opener = wdf_urllib.build_opener(wdf_urllib.HTTPCookieProcessor(CookieJar()))
        wdf_urllib.install_opener(opener)
    except:
        pass
    if not get_uuid():
        print('获取uuid失败')
        return
    showQRImage()
    time.sleep(1)
    while waitForLogin() != '200':
        pass
    os.remove(QRImagePath)
    if not login():
        print('登录失败')
        return
    if not webwxinit():
        print('初始化失败')
        return
    MemberList = webwxgetcontact()
    MemberCount = len(MemberList)
    print('通讯录共%s位好友' % MemberCount)
    ChatRoomName = ''
    result = []
    print('开始查找...')
    group_num=int(math.ceil(MemberCount / float(MAX_GROUP_NUM)))
    for i in range(0, group_num):
        UserNames = []
        NickNames = []
        for j in range(0, MAX_GROUP_NUM):
            if i * MAX_GROUP_NUM + j >= MemberCount:
                break
            Member = MemberList[i * MAX_GROUP_NUM + j]
            UserNames.append(Member['UserName'])
            NickNames.append(Member['NickName'].encode('utf-8'))
        #	进度条
        progress='-'*10
        progress_str='%s'%''.join(map(lambda x:'#',progress[:int((10*(i+1))/group_num)]))
        #print '[',progress_str,''.join('-'*(10-len(progress_str))),']',
        #print '(当前,你被%d人删除,好友共%d人'%(len(result),len(MemberList)),'\r',
        print('[',progress_str,''.join('-'*(10-len(progress_str))),']', end=' ')
        print('(当前,你被%d人删除,好友共%d人'%(len(result),len(MemberList)),'\r',end=' ')
        # print '第%s组...' % (i + 1)
        # print ', '.join(NickNames)
        # print '回车键继续...'
        # raw_input()
        # 新建群组/添加成员
        if ChatRoomName == '':
            (ChatRoomName, DeletedList) = createChatroom(UserNames)
        else:
            DeletedList = addMember(ChatRoomName, UserNames)
        DeletedCount = len(DeletedList)
        if DeletedCount > 0:
            result += DeletedList
        # print '找到%s个被删好友' % DeletedCount
        # raw_input()
        # 删除成员
        deleteMember(ChatRoomName, UserNames)
    # todo 删除群组
    resultNames = []
    for Member in MemberList:
        if Member['UserName'] in result:
            NickName = Member['NickName']
            if Member['RemarkName'] != '':
                NickName += '(%s)' % Member['RemarkName']
            resultNames.append(NickName.encode('utf-8'))
    print('\n---------- 被删除的好友列表 ----------')
    # 过滤emoji
    resultNames=list(map(lambda x:re.sub(r'<span.+/span>','',x),resultNames))
    print('\n'.join(resultNames))
    print('-----------------------------------')


# windows下编码问题修复
# http://blog.csdn.net/heyuxuanzee/article/details/8442718
class UnicodeStreamFilter:  
    def __init__(self, target):
        self.target = target
        self.encoding = 'utf-8'
        self.errors = 'replace'
        self.encode_to = self.target.encoding

    def write(self, s):
        if type(s) == str:
            s = s.decode('utf-8')
        s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
        self.target.write(s)
if sys.stdout.encoding == 'cp936':  
    sys.stdout = UnicodeStreamFilter(sys.stdout)

if __name__ == '__main__' :
    print('本程序的查询结果可能会引起一些心理上的不适,请小心使用...')
    print('回车键继续...')
    try:
        raw_input()
        input = raw_input
    except:
        input()
    main()
    print('回车键结束')
    input()
# vim: noet:sts=8:ts=8:sw=8


