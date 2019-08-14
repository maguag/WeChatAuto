import time
import string
import random
# import re
import hashlib
from urllib import parse
from datetime import datetime
# from collections import OrderedDict
import platform

import itchat
from itchat.content import (
    NOTE,
    TEXT,
    FRIENDS
)
from apscheduler.schedulers.blocking import BlockingScheduler
import requests


IS_OPEN_AUTO_REPLY = True
NLPCHAT_APP_ID = '2120067869'
NLPCHAT_APP_KEY = 'zLjTT94IhjYzO11v'
NLPCHAT_URL = 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat'
MSG_SUFFIX = " ——auto reply by MaguaAI"
LONG_TEXT = string.ascii_letters + string.digits + string.punctuation
wechat_nick_name = ''
HEART_BEAT_INTERVAL_MINUTES = 15


def init_info():
    global wechat_nick_name
    global IS_OPEN_EMAIL_NOTICE
    wechat_nick_name = itchat.search_friends()['NickName']  # 获取此微信号的昵称
    set_note('微信号『{}』登录成功！'.format(wechat_nick_name))
    print('项目初始化已完成...开始正常工作。')
    print('-' * 50)


@itchat.msg_register([TEXT])
def deal_with_msg(msg):
    text = msg["Text"]  # 获取好友发送的话
    userid = msg['FromUserName']  # 获取好友的 uid
    nickname = msg['User']['NickName']
    if IS_OPEN_AUTO_REPLY:  # 是否已开启 AI 自动回复
        reply_text = get_nlp_textchat(text, userid)
        reply_text = reply_text if reply_text else ''
        reply_text = reply_text + MSG_SUFFIX
    else:
       reply_text = ''
    itchat.send(reply_text, userid)
    note = '\n{}发送来的:{}\n自动回复:{}'.format(nickname, text, reply_text)
    set_note(note)


def is_online():
    try:
        if itchat.search_friends():
            return True
    except IndexError:
        return False
    return True


def heart_beat():
    if is_online():
        time.sleep(random.randint(1, 100))
        time_ = datetime.now().strftime('%Y-%m-%d %H:%M:%S  ')
        d = ''.join(random.sample(LONG_TEXT, random.randint(10, 20)))
        note = "定时心跳...{}-{}".format(time_, d)
        set_note(note)
    else:
        exit_callback()


def exit_callback():
    time_ = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    title = '您服务器上的微信「{}」已离线'.format(wechat_nick_name)
    content = '离线时间：{} \n 离线原因：未知'.format(time_)
    # send_mail(title, content)
    set_note(title + content, True)
    stop_scheduler()
    stop_system()


def set_note(note, onle_log=False):
    if not onle_log:
        itchat.send(note, 'filehelper')
    print(note)


def stop_scheduler():
    """ 关闭定时器 """
    if scheduler and scheduler.get_jobs():
        scheduler.shutdown(wait=False)


def stop_system():
    """退出应用"""
    exit(1)


def get_nlp_textchat(text, userId):
    try:
        hash_md5 = hashlib.md5(userId.encode("UTF-8"))
        userId = hash_md5.hexdigest().upper()
        nonce_str = ''.join(random.sample(LONG_TEXT, random.randint(10, 16)))
        time_stamp = int(time.time())
        params = {
            'app_id': NLPCHAT_APP_ID,
            'time_stamp': time_stamp,
            'nonce_str': nonce_str,
            'session': userId,
            'question': text
        }
        params['sign'] = getReqSign(params, NLPCHAT_APP_KEY)
        resp = requests.get(NLPCHAT_URL, params=params)
        if resp.status_code == 200:
            content_dict = resp.json()
            if content_dict['ret'] == 0:
                data_dict = content_dict['data']
                return data_dict['answer']
            else:
                print('获取数据失败:{}'.format(content_dict['msg']))
    except Exception as exception:
        print(str(exception))


def getReqSign(parser, app_key):
    params = sorted(parser.items())
    uri_str = parse.urlencode(params, encoding="UTF-8")
    sign_str = '{}&app_key={}'.format(uri_str, app_key)
    hash_md5 = hashlib.md5(sign_str.encode("UTF-8"))
    return hash_md5.hexdigest().upper()


if __name__ == '__main__':

    if platform.system() in ('Windows', 'Darwin'):
        itchat.auto_login(hotReload=True,
                          loginCallback=init_info, exitCallback=exit_callback)
    else:
        # 命令行显示登录二维码。
        itchat.auto_login(enableCmdQR=2, loginCallback=init_info,
                          exitCallback=exit_callback)
    itchat.run(blockThread=False)

    scheduler = BlockingScheduler()
    scheduler.add_job(heart_beat, 'interval', minutes=HEART_BEAT_INTERVAL_MINUTES)

