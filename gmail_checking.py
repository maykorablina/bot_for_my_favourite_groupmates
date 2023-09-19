import asyncio
import time

from database import Database
from mail_functions import check_email
import aiogram
import sqlite3
from aiogram import Bot, Dispatcher, types, executor
from aiogram import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

db = Database('maya_mail.db')

TOKEN_API = '6394952533:AAH9nlTghSEG-F-P-LCTSN59APZQxybRt6o'
bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def beginning(message):
    while True:
        result = check_email()[0]
        query = db.fetchall('SELECT * FROM mails WHERE id = ?;', values=(result['id'],))
        if len(query) == 0:
            values = [result['id'], result['date'], result['topic'], result['sender'], result['text']]
            db.execute('''
                #         INSERT INTO mails (id, date, topic, sender, text) VALUES (?, ?, ?, ?, ?);
                #     ''', values)
            for a in result['attachments']:
                db.execute('''
                    INSERT INTO attachments (mail_id, attachment) VALUES (?, ?);
                    ''', [result['id'], a])

            text = result['text'][0:100] + +'...\nПродолжение смотрите на другом сайте'
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f"Дата: {result['date']}\nОт: {result['sender']}\nТема: {result['topic']}\n{result['text']}")
            for doc in result['attachments']:
                with open(f'temp/{filename}', 'wb') as f:
                    f.write(file_data)
                await bot.send_document(chat_id=message.from_user.id, document=file)

    result = list(db.fetchall('''SELECT * FROM mails'''))
    # print(result)
    for r in result:
    # result[3] = result[3].replace("<", "(").replace(">", ")")
        files = db.fetchall('SELECT attachment FROM attachments WHERE mail_id = ?;', values=(r[0],))
    # for i in files:
    #     print(i[0])
    # print(result)
        text = r[4][0:500] +'\nПродолжение смотрите на другом сайте'
        await bot.send_message(chat_id=message.from_user.id,
                           text=f'Дата: {r[1]}\nОт: {r[3]}\nТема: {r[2]}\n{text}')
        time.sleep(10)

#
#
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
