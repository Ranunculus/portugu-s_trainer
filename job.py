import schedule
import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

from portugués_trainer import database_operations as database


def token():
    fh = open("telegram.token")
    return fh.readline().rstrip()


def prompt_users():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Учить слова', callback_data='train'))
    user_ids = database.get_users_for_training()
    for user_id in user_ids:
        try:
            bot.send_message(user_id[1], text="Время тренироваться", reply_markup=keyboard)
        except ApiTelegramException as e:
            print(e.result_json)


bot = telebot.TeleBot(token())

schedule.every().day.at("10:00").do(prompt_users)
schedule.every().day.at("13:00").do(prompt_users)
schedule.every().day.at("16:00").do(prompt_users)
schedule.every().day.at("18:00").do(prompt_users)
schedule.every().day.at("20:00").do(prompt_users)

while 1:
    schedule.run_pending()
