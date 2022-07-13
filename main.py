from os import system
try:
    import requests
except:
    system('pip install requests')
try:
    import urllib3
except:
    system('pip install urllib3')

from json import loads
from random import choice, randint
from time import sleep
from threading import Thread
from os import system
try:
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.service import Service
    from selenium import webdriver
except:
    system('pip install selenium')
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.service import Service
    from selenium import webdriver
try:
    from langdetect import detect
except:
    system('pip install langdetect')
    from langdetect import detect
import os
path = os.path.abspath('geckodriver')
urllib3.disable_warnings()

pause = float(input('Введите паузу/кулдаун между отправкой сообщений в секундах: '))
typing_sleep= input('Введите время имитирования печатания сообщения в секундах: ')
n = input('Введите то количество последних сообщений, которые будут парситься в чате.\nЕсли за последние n сообщений вам никто не ответил, то бот отправляет либо случайный реплай, либо случайное сообщение без реплая (шанс 50/50): ')
deleteask = input('Нужно ли удалять сообщение после отправки? y/n: ')
betweentime = input('Введите время задержки между аккаунтами (диапазон или целое значение): ')
msgusing = input('Нужно ли использовать документ msg.txt? y/n: ')

messagelist = []
dstokens =[]
with open('msg.txt', encoding="utf8") as msg:
    lines = msg.readlines()
    for line in lines:
        messagelist.append(line)

with open('tokens.txt', encoding='utf8') as tokens:
    tokenandid = tokens.readlines()
    for token in tokenandid:
        dstokens.append(token.rstrip())
banwords=[]

def get_answer(lastchatmessage):
    try:
        options = Options()
        options.headless = True
        s = Service(path)
        browser = webdriver.Firefox(service=s, options=options)
        browser.get('http://p-bot.ru')
        sleep(2.5)
        browser.implicitly_wait(10)
        inputfield = browser.find_element(By.CSS_SELECTOR, '#user_request')
        inputfield.clear()
        inputfield.send_keys(lastchatmessage)
        say_button = browser.find_element(By.CSS_SELECTOR, '#btnSay').click()
        sleep(3)
        answer = browser.find_element(By.CSS_SELECTOR, '#answer_0').text
        browser.close()
        browser.quit()
        with open('banwords.txt', 'r', encoding='utf8') as banwords:
            banword = banwords.readlines()
            for bwd in banword:
                bwd.rstrip('\n')
                find = answer.strip().find(bwd.rstrip('\n'))
                if find==-1:
                    bb = 0
                else:
                    bb=1
                    break
        if find==-1:
            if answer.find('.')!=-1:
                return(answer[5:-1].lstrip())
            else:
                return (answer[5:].lstrip())
        else:
            print(f'Found banword: [{bwd.strip()}]')
            pass
    except Exception as ex:
        print(ex)
        print("Couldn't send message to pBot")


def send_message(discordtoken, chatid):
    author=''
    havereply=0
    sentmessages = []
    lastsentmessage='белебердадляпервогосообщениялол'
    successfullsend=0
    while True:
        try:
            session = requests.Session()
            session.headers['authorization'] = discordtoken
            r = session.get(f'https://discord.com/api/v9/channels/{chatid}/messages?limit=50')
            username = loads(session.get('https://discordapp.com/api/users/@me', verify=False).text)['username']
            try:
                for id in range(0, int(n)):
                    lastmessage_repliedname = loads(r.text)[id]['mentions']
                    if lastmessage_repliedname == []:
                        pass
                    else:
                        lastmessage_repliedname = loads(r.text)[id]['mentions'][0]['username']
                        if lastmessage_repliedname == username:
                            havereply = 1
                            lastchatmessage = loads(r.text)[id]['content']
                            messageid = loads(r.text)[id]['id']
                            author = loads(r.text)[id]['author']['username']
                            break
                        else:
                            havereply=0
            except IndexError:
                'nothing'
            if havereply==1:
                answer = get_answer(lastchatmessage)
                try:
                    answertocheck = answer.find(lastsentmessage)
                except Exception as Ex:
                    print(f'Sleeping {pause} seconds.')
                    print(Ex)
                    answertocheck=0
                if answertocheck==-1 and username.rstrip()!=author.rstrip():
                    data = {'content': answer, 'message_reference': {"message_id": messageid}, 'tts': False}
                    r = session.post(f'https://discord.com/api/v9/channels/{chatid}/typing', verify=False)
                    sleep(int(typing_sleep))
                    zapros = session.post(f'https://discord.com/api/v9/channels/{chatid}/messages', json=data,verify=False)
                    if zapros.status_code == 200:
                        print(f'Account with the name [{username}] Successfully replied to the user [{author}] with the message: [{answer}]')
                        lastsentmessage = answer
                        successfullsend = 1
                        if deleteask.lower() == 'y':
                            messageid = str(loads(zapros.text)['id'])
                            delete = session.delete(f'https://discord.com/api/v9/channels/{chatid}/messages/{messageid}')
                            print(f'Account with the name [{username}] Deleted message [{answer}].')
                        print(f'Account with the name [{username}] Sleeping {pause} seconds')
                        sleep(pause)
                    elif zapros.status_code==400:
                        print(f"Account with the name [{username}] Couldn't send message. {zapros.status_code} error. Can't send empty message/message with the banword")
                        successfullsend = 0
                    elif zapros.status_code==429:
                        print(f"Account with the name [{username}] Couldn't send message. {zapros.status_code} error. You may have received a ban in the chat. You should check it out ")
                        successfullsend = 0
                    else:
                        print(f"Account with the name [{username}] Couldn't send message. {zapros.status_code} error. Contact with the creator to fix this")
                        successfullsend = 0
            elif msgusing.lower()=='y':
                x = randint(1,2)
                if x==1:
                    try:
                        for id in range(0, randint(5, 30)):
                            lastmessage_author = loads(r.text)[id]['author']['username']
                            if lastmessage_author =='':
                                pass
                            else:
                                lastchatmessage = loads(r.text)[id]['content']
                                messageid = loads(r.text)[id]['id']
                                author = loads(r.text)[id]['author']['username']
                                break
                        answer = get_answer(lastchatmessage)
                        try:
                            answertocheck = answer.find(lastsentmessage)
                        except Exception as Ex:
                            answertocheck=0
                            print(Ex)
                        if answertocheck == -1 and username.rstrip().find(author.rstrip()) == -1:
                            data = {'content': answer, 'message_reference': {"message_id": messageid}, 'tts': False}
                            r = session.post(f'https://discord.com/api/v9/channels/{chatid}/typing', verify=False)
                            sleep(int(typing_sleep))
                            zapros = session.post(f'https://discord.com/api/v9/channels/{chatid}/messages', json=data,verify=False)
                            if zapros.status_code == 200:
                                print(f'Account with the name [{username}] Successfully replied to the user [{author}] with the message: [{answer}]')
                                lastsentmessage = answer
                                if deleteask.lower() == 'y':
                                    messageid = str(loads(zapros.text)['id'])
                                    delete = session.delete(f'https://discord.com/api/v9/channels/{chatid}/messages/{messageid}')
                                    print(f'Account with the name [{username}] Deleted message [{answer}].')
                                print(f'Account with the name [{username}] Sleeping {pause} seconds')
                                sleep(pause)
                            elif zapros.status_code == 400:
                                print(f"Account with the name [{username}] Couldn't send message. {zapros.status_code} error. Can't send empty message/message with the banword")
                                successfullsend = 0
                            elif zapros.status_code == 429:
                                print(f"Account with the name [{username}] Couldn't send message. {zapros.status_code} error. You may have received a ban in the chat. You should check it out ")
                                successfullsend = 0
                            else:
                                print(f"Account with the name [{username}] Couldn't send message. {zapros.status_code} error. Contact with the creator to fix this")
                                successfullsend = 0
                    except IndexError:
                        print('index error')
                    except Exception as Ex:
                        print(Ex)
                else:
                    try:
                        r = session.post(f'https://discord.com/api/v9/channels/{chatid}/typing', verify=False)
                        sleep(int(typing_sleep))
                        if messagelist!=[]:
                            randommessage = messagelist[0]
                            send = randommessage.rstrip()
                            messagelist.pop(0)
                        if len(messagelist)<=1:
                            messagelist.clear()
                            with open('msg.txt', encoding="utf8") as msg:
                                lines = msg.readlines()
                                for line in lines:
                                    messagelist.append(line)
                        if send.find(lastsentmessage)==-1:
                            data = {'content': send, 'tts': False}
                            zapros = session.post(f'https://discord.com/api/v9/channels/{chatid}/messages', json=data, verify=False)
                            if zapros.status_code==200:
                                print(f'Account with the name [{username}] Successfully sent random message [{send}] without reply')
                                if deleteask.lower() == 'y':
                                    messageid = str(loads(zapros.text)['id'])
                                    lastsentmessage=send
                                    delete = session.delete(f'https://discord.com/api/v9/channels/{chatid}/messages/{messageid}')
                                    print(f'Account with the name [{username}] Deleted message [{answer}].')
                            elif zapros.status_code == 400:
                                print(
                                    f"Account with the name [{username}] Couldn't send message. {zapros.status_code} error. Can't send empty message/message with the banword")
                                successfullsend = 0
                            elif zapros.status_code == 429:
                                print(
                                    f"Account with the name [{username}] Couldn't send message. {zapros.status_code} error. You may have received a ban in the chat. You should check it out ")
                                successfullsend = 0
                            else:
                                print(
                                    f"Account with the name [{username}] Couldn't send message. {zapros.status_code} error. Contact with the creator to fix this")
                                successfullsend = 0
                            print(f'Account with the name [{username}] Sleeping {pause} seconds')
                            sleep((pause))
                        else:
                            'nothing'
                    except IndexError:
                        'nothing'
                    except Exception as Ex:
                        print(Ex)
            else:
                try:
                    for id in range(0, randint(5, 30)):
                        lastmessage_author = loads(r.text)[id]['author']['username']
                        if lastmessage_author == '':
                            pass
                        else:
                            lastchatmessage = loads(r.text)[id]['content']
                            messageid = loads(r.text)[id]['id']
                            author = loads(r.text)[id]['author']['username']
                            break
                    answer = get_answer(lastchatmessage)
                    try:
                        answertocheck = answer.find(lastsentmessage)
                    except Exception as Ex:
                        answertocheck = 0
                        print(Ex)
                    if answertocheck == -1 and username.rstrip().find(author.rstrip()) == -1:
                        data = {'content': answer, 'message_reference': {"message_id": messageid}, 'tts': False}
                        r = session.post(f'https://discord.com/api/v9/channels/{chatid}/typing', verify=False)
                        sleep(int(typing_sleep))
                        zapros = session.post(f'https://discord.com/api/v9/channels/{chatid}/messages', json=data,
                                              verify=False)
                        if zapros.status_code == 200:
                            print(
                                f'Account with the name [{username}] Successfully replied to the user [{author}] with the message: [{answer}]')
                            lastsentmessage = answer
                            if deleteask.lower() == 'y':
                                messageid = str(loads(zapros.text)['id'])
                                delete = session.delete(
                                    f'https://discord.com/api/v9/channels/{chatid}/messages/{messageid}')
                                print(f'Account with the name [{username}] Deleted message [{answer}].')
                            print(f'Account with the name [{username}] Sleeping {pause} seconds')
                            sleep(pause)
                        elif zapros.status_code == 400:
                            print(
                                f"Account with the name [{username}] Couldn't send message. {zapros.status_code} error. Can't send empty message/message with the banword")
                            successfullsend = 0
                        elif zapros.status_code == 429:
                            print(
                                f"Account with the name [{username}] Couldn't send message. {zapros.status_code} error. You may have received a ban in the chat. You should check it out ")
                            successfullsend = 0
                        else:
                            print(
                                f"Account with the name [{username}] Couldn't send message. {zapros.status_code} error. Contact with the creator to fix this")
                            successfullsend = 0
                except IndexError:
                    print('index error')
                except Exception as Ex:
                    print(Ex)
        except Exception as Ex:
            print(Ex)


if __name__=='__main__':
    for i in range(len(dstokens)):
        while dstokens:
            for data in dstokens:
                dstokens.pop(0)
                data = data.strip(':')
                discordtoken, chatid = data.split(':')
                someth = Thread(target=send_message, args=(discordtoken, chatid))
                someth.start()
                if '-' in betweentime:
                    betweentimedelay = betweentime.split('-')
                    firststart_sleeping = randint(int(betweentimedelay[0]), int(betweentimedelay[1]))
                else:
                    firststart_sleeping = betweentime
                sleep(int(firststart_sleeping))