import re
import time
from threading import Thread

import schedule
import pendulum
import requests
from bs4 import BeautifulSoup
import telebot

from models import User
from faculty import faculty

token = 'TELEGRAM_API_TOKEN'
bot = telebot.TeleBot(token)


def get_html(group, day):
    params = {'faculty': '0', 'group': group.encode('cp1251'),
              'sdate': day, 'edate': day, 'n': '700'}
    r = requests.post("http://195.95.232.162:8082/cgi-bin/timetable.cgi",
                      data=params)
    r.encoding = 'cp1251'
    return r.text


def fetch_timetable(text):
    soup = BeautifulSoup(text, "html.parser")
    table = soup.find_all('table')
    shed = ''
    for i, val1 in enumerate(table):
        el1 = val1.find_all('td')
        for j, e in enumerate(el1[1::2]):
            if e.text:
                semicoloms = re.findall('\([^\)]*\)', e.text)
                if len(semicoloms) > 1:
                    s = e.text.replace(semicoloms[1], '')
                else:
                    s = e.text
                shed += str(j + 1) + ' пара ' + s + '\n'
    return shed


def send_subscribers():
    users = User.objects(subscribe=True)
    for user in users:
        group = user.group
        chat_id = user.chat_id
        now = pendulum.now()
        day = now.format('DD.MM.YYYY', formatter='alternative')
        html = get_html(group, day)
        bot.send_message(chat_id, fetch_timetable(html))


schedule.every().day.at("7:30").do(send_subscribers)


def event_loopy():
    while True:
        schedule.run_pending()
        time.sleep(60)


Thread(target=event_loopy).start()


@bot.message_handler(commands=['start'])
def handle_start(message):
    user = User.get_by_chat_id(message.chat.id)
    if user is None:
        User(first_name=message.chat.first_name, last_name=message.chat.last_name,
             chat_id=message.chat.id, username=message.chat.username).save()

    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row("Час пар")
    bot.send_message(message.chat.id, 'Напишыть свій факультет\n'
                                      'Приклади: "КТ-151", "кт-151", "М-54", "мАВ-14", "МБА-055"',
                     reply_markup=user_markup)


@bot.message_handler(func=lambda mess: mess.text.upper() in faculty, content_types=['text'])
def handle_text(message):
    user = User.get_by_chat_id(message.chat.id)
    user.group = message.text
    user.save()

    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row("Розклад на сьогодні")
    user_markup.row("Розклад на завтра")
    user_markup.row("Підписатись")
    user_markup.row("Час пар")
    bot.send_message(message.chat.id, 'Група встановлена', reply_markup=user_markup)


@bot.message_handler(func=lambda mess: 'Розклад на сьогодні' == mess.text, content_types=['text'])
def handle_text(message):
    group = User.get_by_chat_id(message.chat.id).group
    now = pendulum.now()
    day = now.format('DD.MM.YYYY', formatter='alternative')
    html = get_html(group, day)
    bot.send_message(message.chat.id, fetch_timetable(html))


@bot.message_handler(func=lambda mess: 'Розклад на завтра' == mess.text, content_types=['text'])
def handle_text(message):
    group = User.get_by_chat_id(message.chat.id).group
    now = pendulum.now()
    now = now.add(days=1)
    day = now.format('DD.MM.YYYY', formatter='alternative')
    html = get_html(group, day)
    bot.send_message(message.chat.id, fetch_timetable(html))


@bot.message_handler(func=lambda mess: 'Час пар' == mess.text, content_types=['text'])
def handle_text(message):
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_photo(message.chat.id, open('/home/andriy/PycharmProjects/shedule_bot/shed.jpg', 'rb'))


@bot.message_handler(func=lambda mess: 'Підписатись' == mess.text, content_types=['text'])
def handle_text(message):
    user = User.get_by_chat_id(message.chat.id)
    user.subscribe = True
    user.save()
    bot.send_message(message.chat.id, 'Ви підписальсь на розсилку повідомлень об 7:30')


if __name__ == '__main__':
    bot.polling()
