import telebot
from fuzzywuzzy import fuzz as fuzzy_search
from telebot import types

from portugués_trainer import database_operations as database


def token():
    fh = open("telegram.token")
    return fh.readline().rstrip()


bot = telebot.TeleBot(token())

answers = {}


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
        train_next_word_prompt(call.message.chat)
    elif call.data == "new":
        add_new_word_prompt(call.message.chat)


def add_new_word_prompt(chat):
    bot.send_message(chat.id, "Введи через запятую:слово,произношение,перевод")


def train_next_word_prompt(chat):
    words_to_train = database.next_word_for_training()
    if len(words_to_train) == 0:
        bot.send_message(chat.id, "Молодец! Пока все слова повторены")
    else:
        next_word_for_training = words_to_train[0]
        answers[chat.username] = (next_word_for_training[0], next_word_for_training[1])
        bot.send_message(chat.id, next_word_for_training[3])


@bot.message_handler(content_types=['text'])
def handle_word(message):
    message_split = message.text.split(",")
    if len(message_split) == 3:
        database.create_new_word(message_split[0], message_split[1], message_split[2])
        add_new_word_prompt(message.chat)
    else:
        answer_tuple = answers[message.chat.username]
        answer = answer_tuple[1]
        ratio = fuzzy_search.ratio(answer, message.text)
        if ratio == 100:
            bot.send_message(message.chat.id, "Отлично!")
        else:
            # todo: hints?
            bot.send_message(message.chat.id, f"Правильный ответ: {answer}")

        database.save_training_result(answer_tuple[0], ratio)
        train_next_word_prompt(message.chat)


bot.polling()
