from wxpy import *

bot = Bot(cache_path=True)

print("开启好友轰炸功能-MaguaG")
# global s

def send_news():
        while(True):
                name = input('请输入好有名字：')
                inn = input('请输入消息内容：')
                # times = input('请输入消息次数：')
                try:
                        my_friend = bot.friends().search(str(name))[0]
                        for i in range(44):
                                my_friend.send(str(inn))
                        print("已给%s发送%s44次"%(name, inn))
                except:
                        # my_friend = bot.friends().search('')[0]
                        # my_friend.send(u"今天消息发送失败了")
                        print('11')
                # s = input("继续吗，True？False？")
if __name__ == "__main__":
	send_news()
