import telebot
from fuzzywuzzy import fuzz as fuzzy_search
from telebot import types
from portugués_trainer import database_operations as database


def token():
    fh = open("telegram.token")
    return fh.readline().rstrip()


bot = telebot.TeleBot(token())
database.init_database()


def delete_session_for_user(user_id):
    database.delete_session_for_user(user_id)


def remove_session_word_for_user_and_increment_words_count(user_id):
    database.remove_session_word_for_user(user_id)


@bot.message_handler(commands=['start', 'restart'])
def start_message(message):
    keyboard = types.InlineKeyboardMarkup()
    user_id = message.from_user.id
    database.create_user_if_doesnt_exist(user_id, message.from_user.first_name)
    database.create_session_for_user_if_doesnt_exist(user_id)
    database.create_settings_for_user_if_doesnt_exist(user_id)
    if database.has_words_to_train(user_id):
        bot_train_option(keyboard)
    else:
        add_existing_prompt = types.InlineKeyboardButton(text='Скопировать текущую версию словаря для тренировок',
                                                         callback_data='add_existing')
        keyboard.add(add_existing_prompt)
    bot_add_new_word(keyboard)
    bot_show_settings_prompt(keyboard)
    bot.send_message(user_id, text=f"{message.from_user.first_name}, что будем делать?", reply_markup=keyboard)


def bot_add_new_word(keyboard):
    keyboard.add(types.InlineKeyboardButton(text='Добавим новые слова вручную', callback_data='new'))


def bot_train_option(keyboard):
    keyboard.add(types.InlineKeyboardButton(text='Учить слова', callback_data='train'))


def add_existing_words_for_user_training(user_id):
    database.create_trainings_of_all_words_for_user(user_id)


def bot_show_settings_prompt(keyboard):
    keyboard.add(types.InlineKeyboardButton(text='Показать настройки', callback_data='show_settings'))


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    user_id = call.from_user.id
    if call.data == "train":
        # delete_session_for_user(user_id)
        database.remove_words_count_for_user(user_id)
        train_next_word_prompt(call.message.chat, call.from_user.id)
    elif call.data == "new":
        add_new_word_prompt(call.message.chat)
    elif call.data == "add_existing":
        add_existing_words_for_user_training(user_id)
        keyboard = types.InlineKeyboardMarkup()
        bot_train_option(keyboard)
        bot_add_new_word(keyboard)
        bot.send_message(user_id, text="Готово! Что дальше?", reply_markup=keyboard)
    elif call.data == "show_settings":
        settings = database.get_settings_for_user(user_id)
        bot.send_message(user_id, text=f"Количество слов в одной учебной сессии {settings[2]}")


def add_new_word_prompt(chat):
    bot.send_message(chat.id, "Введи через запятую:слово,произношение,перевод")


def train_next_word_prompt(chat, user_id):
    if database.check_session(user_id):
        bot.send_message(chat.id, "Молодец! Учебная сессия завершена")
        return
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
    elif len(message_split) == 2:
        bot.send_message(message.chat.id, f"Неправильный формат сообщения")
    else:
        current_session = database.get_session_for_user(message.from_user.id)
        answer = database.get_word(current_session[2])
        ratio = fuzzy_search.ratio(answer[1].lower(), message.text.lower())
        if ratio == 100:
            bot.send_message(message.chat.id, "Отлично!")
        else:
            if answer[1].lower().endswith(message.text.lower()):
                bot.send_message(message.chat.id, f"А артикль?")
                return
            elif ratio > 80:
                bot.send_message(message.chat.id, f"Почти) Попробуй ещё раз")
                return
            else:
                bot.send_message(message.chat.id, f"Правильный ответ: {answer[1]}")

        database.save_training_result(message.from_user.id, answer[0], ratio)
        remove_session_word_for_user_and_increment_words_count(message.from_user.id)
        train_next_word_prompt(message.chat, message.from_user.id)


bot.polling()
