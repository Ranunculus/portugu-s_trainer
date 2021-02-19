import schedule
import telebot
from telebot import types
from portugués_trainer import database_operations as database


def token():
    fh = open("telegram.token")
    return fh.readline().rstrip()


def prompt_users():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Учить слова', callback_data='train'))
    user_ids = database.get_users_for_training()
    for user_id in user_ids:
        bot.send_message(user_id[1], text="Время тренироваться", reply_markup=keyboard)


bot = telebot.TeleBot(token())


schedule.every(1).hour.do(prompt_users)

while 1:
    schedule.run_pending()
