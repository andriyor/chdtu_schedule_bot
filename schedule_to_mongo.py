from bs4 import BeautifulSoup
import re
from mongoengine import *
connect('shedule')


class Timetable(Document):
    lesson_date = StringField()
    order = IntField()
    weekday = IntField()
    types = StringField()
    subject = StringField()
    teacher = StringField()
    classroom = StringField()


def ftch_data(s, word, dot):
    semicoloms = re.findall('\([^\)]*\)', s)
    types = semicoloms[0]
    subject = (s[s.find(')') + 2:s.find(word) - 1])
    indices = [i for i, x in enumerate(s) if x == "."]
    teachers = (s[s.find(word):indices[dot] - 2])
    auditori = (s[indices[dot] - 1:])
    if len(semicoloms) > 1:
        potok = semicoloms[1]
        auditori = auditori[:auditori.index(potok) - 1]
    return types, subject, teachers, auditori


def parse_string(s):
    if 'асистент' in s:
        return ftch_data(s, 'асистент', 2)
    elif 'доцент' in s:
        return ftch_data(s, 'доцент', 2)
    elif 'ст. викладач' in s:
        return ftch_data(s, 'ст. викладач', 3)
    elif 'викладач' in s:
        return ftch_data(s, 'викладач', 2)

soup = BeautifulSoup(open("html/all.html"), "html.parser")

table = soup.find_all('table')
h4 = soup.find_all('h4')[3:]

d = {'Понеділок': 1, 'Вівторок': 2, 'Середа': 3, 'Четвер': 4, "П'ятниця": 5}

for timetable, date in zip(table, h4):
    lesson_info = timetable.find_all('td')[1::2]
    weekday = date.small.text
    lesson_date = date.find(text=True, recursive=False)
    for i, info in enumerate(lesson_info):
        if info.text:
            types, subject, teacher, classroom = parse_string(info.text)
            print(i + 1, ' пара', info.text)

            Timetable(lesson_date=lesson_date, order=i + 1, weekday=d[weekday],
                      types=types, subject=subject, teacher=teacher,
                      classroom=classroom).save()

