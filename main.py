import pandas as pd
import aiogram
import asyncio
import time

# from database import Database
# from quickstart import check_email
import aiogram
import sqlite3
from aiogram import Bot, Dispatcher, types, executor
from aiogram import executor
import timetable_processing as tp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# db = Database('maya_mail.db')

TOKEN_API = '6394952533:AAH9nlTghSEG-F-P-LCTSN59APZQxybRt6o'
bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def beginning(message):
    while True:
        base_timetable = tp.get_timetable(key='1oZ1epXfxBrHG7crr5nMl8WN7rbhjJJWFD1FHBS9pXJk')
        time.sleep(20)
        temp_timetable = tp.get_timetable(key='1oZ1epXfxBrHG7crr5nMl8WN7rbhjJJWFD1FHBS9pXJk')
        new_timetable = tp.check_on_updates(base_timetable, temp_timetable)
        text
        if new_day_table:
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'Дата: {r[1]}\nОт: {r[3]}\nТема: {r[2]}\n{text}')
#
#
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
