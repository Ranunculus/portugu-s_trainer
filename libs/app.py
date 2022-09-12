from fuzzywuzzy import fuzz as fuzzy_search

from portugués_trainer.libs import database_operations as database

database.init_database()


def delete_session_for_user(user_id):
    database.delete_session_for_user(user_id)


def remove_session_word_for_user_and_increment_words_count(user_id):
    database.remove_session_word_for_user(user_id)


def add_existing_words_for_user_training(user_id):
    database.create_trainings_of_all_words_for_user(user_id)


def train_next_word_prompt(user_id):
    if database.check_session(user_id):
        return ["", "", "", "Молодец! Учебная сессия завершена"]
    words_to_train = database.next_word_for_training(user_id)
    if len(words_to_train) == 0:
        return ["", "", "", "Молодец! Пока все слова повторены"]
    else:
        next_word_for_training = words_to_train[0]
        database.save_session_for_user(user_id, next_word_for_training[0])
        return next_word_for_training


def find_picture(user_id, word_id):
    return database.find_picture(user_id, word_id)


def handle_user_response(message_split, user_id, text_lower, image_bytes):
    if len(message_split) == 3:
        word_id = database.create_new_word(user_id, message_split[0], message_split[1], message_split[2])
        if image_bytes:
            database.add_image_for_word_and_user(word_id, user_id, image_bytes)
    elif len(message_split) == 2:
        return HandlerResult(f"Неправильный формат сообщения")
    else:
        current_session = database.get_session_for_user(user_id)
        if current_session[2] is None:
            return HandlerResult("Session is not valid, restart")
        answer = database.get_word(current_session[2])
        ratio = fuzzy_search.ratio(answer[1].lower(), text_lower)
        if ratio == 100:
            result = "Отлично!"
        else:
            if answer[1].lower().endswith(text_lower):
                return HandlerResult(f"А артикль?")
            elif ratio > 80:
                return HandlerResult(f"Почти) Попробуй ещё раз")
            else:
                result = f"Правильный ответ: {answer[1]}"

        database.save_training_result(user_id, answer[0], ratio)
        remove_session_word_for_user_and_increment_words_count(user_id)
        return HandlerResult(result, True)


class HandlerResult:
    message = ''
    show_word_prompt = False

    def __init__(self, name, show_word_prompt=False):
        self.message = name
        self.show_word_prompt = show_word_prompt


def train(user_id):
    # delete_session_for_user(user_id)
    database.remove_words_count_for_user(user_id)


def get_settings(user_id):
    database.get_settings_for_user(user_id)


def start(user_id, first_name):
    database.create_user_if_doesnt_exist(user_id, first_name)
    database.create_session_for_user_if_doesnt_exist(user_id)
    database.create_settings_for_user_if_doesnt_exist(user_id)
    return database.has_words_to_train(user_id)
