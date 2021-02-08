import telebot
from telebot import types


def token():
    fh = open("telegram.token")
    return fh.readline().rstrip()


bot = telebot.TeleBot(token())


@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = types.InlineKeyboardMarkup()
    train_option = types.InlineKeyboardButton(text='Учить слова', callback_data='train')
    keyboard.add(train_option)
    add_new_option = types.InlineKeyboardButton(text='Добавим новые слова', callback_data='new')
    keyboard.add(add_new_option)
    bot.send_message(message.from_user.id, text="Что будем делать?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "train":
        bot.send_message(call.message.chat.id, 'Запомню : )')
    elif call.data == "new":
        bot.send_message(call.message.chat.id, 'В разработке')


bot.polling()
