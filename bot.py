import telebot
from telebot import types
import requests

from portugués_trainer.libs import app


def token():
    fh = open("telegram.token")
    return fh.readline().rstrip()


bot = telebot.TeleBot(token())


#keyboard
def bot_add_new_word(keyboard):
    keyboard.add(types.InlineKeyboardButton(text='Добавим новые слова вручную', callback_data='new'))


def bot_train_option(keyboard):
    keyboard.add(types.InlineKeyboardButton(text='Учить слова', callback_data='train'))


def bot_show_settings_prompt(keyboard):
    keyboard.add(types.InlineKeyboardButton(text='Показать настройки', callback_data='show_settings'))


def add_new_word_prompt(chat):
    bot.send_message(chat.id, "Введи через запятую:слово,произношение,перевод")


# handlers
@bot.message_handler(commands=['start', 'restart'])
def start_message(message):
    keyboard = types.InlineKeyboardMarkup()
    user_id = message.from_user.id
    has_words_to_train = app.start(user_id, message.from_user.first_name)
    if has_words_to_train:
        bot_train_option(keyboard)
    else:
        add_existing_prompt = types.InlineKeyboardButton(text='Скопировать текущую версию словаря для тренировок',
                                                         callback_data='add_existing')
        keyboard.add(add_existing_prompt)
    bot_add_new_word(keyboard)
    bot_show_settings_prompt(keyboard)
    bot.send_message(user_id, text=f"{message.from_user.first_name}, что будем делать?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    user_id = call.from_user.id
    if call.data == "train":
        app.train(user_id)
        prompt = app.train_next_word_prompt(call.from_user.id)
        picture = app.find_picture(user_id, prompt[0])
        if picture:
            bot.send_photo(call.message.chat.id, picture, prompt[3])
        else:
            bot.send_message(call.message.chat.id, prompt[3])
    elif call.data == "new":
        add_new_word_prompt(call.message.chat)
    elif call.data == "add_existing":
        app.add_existing_words_for_user_training(user_id)
        keyboard = types.InlineKeyboardMarkup()
        bot_train_option(keyboard)
        bot_add_new_word(keyboard)
        bot.send_message(user_id, text="Готово! Что дальше?", reply_markup=keyboard)
    elif call.data == "show_settings":
        settings = app.get_settings(user_id)
        bot.send_message(user_id, text=f"Количество слов в одной учебной сессии {settings[2]}")


# @bot.message_handler(content_types=['text'])
@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_word(message):
    print(message)
    print(message.chat.id)
    print(message.from_user.id)

    message_split = None
    text = None
    image_bytes = None
    if message.photo:
        image_bytes = get_image(message)
        message_split = message.caption.split(",", 2)
    else:
        message_split = message.text.split(",", 2)
        text = message.text.lower()
    result = app.handle_user_response(message_split, message.from_user.id, text, image_bytes)
    if len(message_split) == 3:
        add_new_word_prompt(message.chat)
    if result:
        bot.send_message(message.chat.id, result.message)
        if result.show_word_prompt:
            bot.send_message(message.chat.id, app.train_next_word_prompt(message.from_user.id))


def get_image(message):
    file_id = message.json['photo'][3]['file_id']
    print(file_id)
    # Get file_path
    photo = get_json('getFile', params={"chat_id": message.chat.id, "file_id": file_id})
    file_path = photo['result']['file_path']
    response = requests.get('https://api.telegram.org/file/bot%s/%s' % (token(), file_path))
    return response.content


def get_json(method_name, *args, **kwargs):
    return make_request('get', method_name, *args, **kwargs)


def make_request(method, method_name, *args, **kwargs):
    response = getattr(requests, method)(
        'https://api.telegram.org/bot%s/%s' % (token(), method_name),
        *args, **kwargs
    )
    if response.status_code > 200:
        raise print(response)
    return response.json()


bot.polling()
