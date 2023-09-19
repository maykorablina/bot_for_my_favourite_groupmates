import pandas as pd
from aiogram import Bot, Dispatcher, types, executor
import timetable_processing as tp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
# from aiogram.filters.command import Command
# db = Database('maya_mail.db')
import time

TOKEN_API = 'hidden'
bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

# лучше используй aiogram версии 2.7, потому что версия 3 еще не доделана, и работает нестабильно

@dp.message_handler(commands=['start'])
async def beginning(message):
    # я заменила while true на флаг, если расписание все таки будет изменено
    # то флаг поменяется на false, и произойдет выход их цикла while
    flag = True
    while flag:
        #  мы будем проверять обновления каждый час, так проще
        # тут получаем датафрейм с расписанием и ждем час, чтобы сделать проверку на изменения
        base_timetable = tp.get_timetable(key='1ylzvoNdYh5TKr248rEWiGCvcLcuvDnDBQjep4i1x9cU')
        time.sleep(3600)
        temp_timetable = tp.get_timetable(key='1ylzvoNdYh5TKr248rEWiGCvcLcuvDnDBQjep4i1x9cU')
        new_timetable = tp.check_on_updates(base_timetable, temp_timetable)
        # если изменения есть, то мы входим в ксловия
        if new_timetable != tp.get_rows_as_lists(temp_timetable):
            # тут получаем уникальные дни недели
            days_of_week = list(set([x[0] for x in new_timetable]))
            to_send = []
            # а тут мы записываем расписания всех дней в список
            # \n это символ перехода на новую строку
            for day in days_of_week:
                text = f'День недели: {day}\n'
                for line in new_timetable:
                    # new_timetablet = new_timetable[new_timetable['day'] == day][['timeslot', '233_2']].fillna(value='okno')

                    # for _, row in t.iterrows():
                    #     row = list(row)
                    text += f'{line[1]} -- {line[2]}\n'
                    text = text.replace("nan", "OKNO")
                to_send.append(text)
            # меняем флаг на false чтобы выйти из цикла
            flag = False
            print(to_send) #чисто для нас инфа в консоль
    # пишем, что у нас есть изменения в расписании
    await bot.send_message(chat_id=message.from_user.id,
                           text='У НАС ИЗМЕНЕНИЯ В РАСПИСАНИИ')
    # а тут отправляем расписания, для каждого дня отдельным сообщением
    for text in to_send:
        await bot.send_message(chat_id=message.from_user.id,
                                           text=text)
        time.sleep(1)
    # а тут просто вызываем эту же функцию внутри самой себя
    # это называется рекурсия, и это как раз та вещь, про которую я забыла в прошлом...
    beginning(message)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
