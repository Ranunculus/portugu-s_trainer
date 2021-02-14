import telebot
from fuzzywuzzy import fuzz as fuzzy_search
from telebot import types
from portugués_trainer import database_operations as database


def token():
    fh = open("telegram.token")
    return fh.readline().rstrip()


bot = telebot.TeleBot(token())
database.init_database()


@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = types.InlineKeyboardMarkup()
    user_id = message.from_user.id
    database.create_user_if_doesnt_exist(user_id, message.from_user.first_name)
    if database.has_words_to_train(user_id):
        bot_train_option(keyboard)
    else:
        add_existing_prompt = types.InlineKeyboardButton(text='Скопировать текущую версию словаря для тренировок', callback_data='add_existing')
        keyboard.add(add_existing_prompt)
    bot_add_new_word(keyboard)
    bot.send_message(user_id, text=f"{message.from_user.first_name}, что будем делать?", reply_markup=keyboard)


def bot_add_new_word(keyboard):
    keyboard.add(types.InlineKeyboardButton(text='Добавим новые слова вручную', callback_data='new'))


def bot_train_option(keyboard):
    keyboard.add(types.InlineKeyboardButton(text='Учить слова', callback_data='train'))


def add_existing_words_for_user_training(user_id):
    database.create_trainings_of_all_words_for_user(user_id)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "train":
        train_next_word_prompt(call.message.chat, call.from_user.id)
    elif call.data == "new":
        add_new_word_prompt(call.message.chat)
    elif call.data == "add_existing":
        user_id = call.from_user.id
        add_existing_words_for_user_training(user_id)
        keyboard = types.InlineKeyboardMarkup()
        bot_train_option(keyboard)
        bot_add_new_word(keyboard)
        bot.send_message(user_id, text="Готово! Что дальше?", reply_markup=keyboard)


def add_new_word_prompt(chat):
    bot.send_message(chat.id, "Введи через запятую:слово,произношение,перевод")


def train_next_word_prompt(chat, user_id):
    words_to_train = database.next_word_for_training(user_id)
    if len(words_to_train) == 0:
        bot.send_message(chat.id, "Молодец! Пока все слова повторены")
    else:
        next_word_for_training = words_to_train[0]
        database.save_session_for_user(user_id, next_word_for_training[0])
        bot.send_message(chat.id, next_word_for_training[3])


@bot.message_handler(content_types=['text'])
def handle_word(message):
    message_split = message.text.split(",")
    if len(message_split) == 3:
        database.create_new_word(message.from_user.id, message_split[0], message_split[1], message_split[2])
        add_new_word_prompt(message.chat)
    else:
        current_session = database.get_session_for_user(message.from_user.id)
        answer = database.get_word(current_session[2])
        ratio = fuzzy_search.ratio(answer[1], message.text)
        if ratio == 100:
            bot.send_message(message.chat.id, "Отлично!")
        else:
            # todo: hints?
            bot.send_message(message.chat.id, f"Правильный ответ: {answer[1]}")

        database.save_training_result(message.from_user.id, answer[0], ratio)
        database.delete_session_for_user(message.from_user.id)
        train_next_word_prompt(message.chat, message.from_user.id)


bot.polling()
