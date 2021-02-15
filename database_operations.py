import datetime
import sqlite3


def get_connection():
    return sqlite3.connect('vocabulary-portuguese.sqlite')


def init_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS Words
        (id INTEGER PRIMARY KEY, word TEXT UNIQUE, transcription TEXT, translation TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Users
        (id INTEGER PRIMARY KEY, 
        first_name TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Trainings
        (id INTEGER PRIMARY KEY, 
        word_id INTEGER, 
        user_id INTEGER,
        successes INTEGER, 
        failures INTEGER, 
        next_training_date INTEGER,
        FOREIGN KEY(word_id) REFERENCES Words(id),
        FOREIGN KEY(user_id) REFERENCES Users(id),
        UNIQUE(word_id, user_id))''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Sessions
        (id INTEGER PRIMARY KEY, 
        user_id INTEGER,
        word_id INTEGER,
        FOREIGN KEY(word_id) REFERENCES Words(id),
        FOREIGN KEY(user_id) REFERENCES Users(id))''')

    cur.close()
    conn.close()


def create_new_word(user_id, word, transcription, translation):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT OR IGNORE INTO Words (word, transcription, translation) VALUES ( ?, ?, ? )',
                   (word, transcription, translation))

    word_id = cursor.execute('SELECT id FROM Words WHERE word = (?)', (word,)).fetchall()
    cursor.execute('INSERT OR IGNORE INTO Trainings (user_id, word_id, successes, failures) VALUES ( ?, ?, ?, ? )',
                   (user_id, word_id[0][0], 0, 0))
    connection.commit()
    cursor.close()
    connection.close()


def list_all():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Words")

    rows = cursor.fetchall()

    cursor.close()
    connection.close()
    return rows


def list_words_for_training(user_id, words_amount):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        f"SELECT word_id FROM Trainings WHERE (next_training_date IS NULL OR next_training_date < {datetime.datetime.now().timestamp()}) AND user_id = {user_id} ORDER BY RANDOM() LIMIT {words_amount}")

    word_ids = cursor.fetchall()

    rows = []
    if len(word_ids) > 0:
        result = []
        for t in word_ids:
            result.append(t[0])
        join = ','.join(['?'] * len(result))
        query = f"SELECT * FROM Words WHERE id IN ({join})"
        rows = cursor.execute(query, result).fetchall()

    cursor.close()
    connection.close()
    return rows


def next_word_for_training(user_id):
    return list_words_for_training(user_id, 1)


def save_training_result(user_id, word_id, ratio):
    connection = get_connection()
    cursor = connection.cursor()
    if ratio == 100:
        cursor.execute('UPDATE Trainings SET successes = successes + 1, next_training_date = ? WHERE word_id = ? and user_id = ?',
                       ((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp(), word_id, user_id, ))
    elif ratio > 85:
        cursor.execute('UPDATE Trainings SET failures = failures + 1, next_training_date = ? WHERE word_id = ? and user_id = ?',
                       ((datetime.datetime.now() + datetime.timedelta(minutes=5)).timestamp(), word_id, user_id, ))
    else:
        cursor.execute('UPDATE Trainings SET failures = failures + 1, next_training_date = ? WHERE word_id = ? and user_id = ?',
                       ((datetime.datetime.now() + datetime.timedelta(minutes=1)).timestamp(), word_id, user_id, ))

    connection.commit()
    cursor.close()
    connection.close()


def create_user_if_doesnt_exist(telegram_user_id, telegram_user_first_name):
    write_data('INSERT OR IGNORE INTO Users (id, first_name) VALUES ( ?, ? )', (telegram_user_id, telegram_user_first_name))


def has_words_to_train(telegram_user_id):
    connection = get_connection()
    cursor = connection.cursor()
    trainings = cursor.execute(
        f"SELECT * FROM Trainings t JOIN Users u on t.user_id = u.id WHERE u.id = {telegram_user_id} LIMIT 1").fetchall()
    cursor.close()
    connection.close()
    return len(trainings) > 0


def create_trainings_of_all_words_for_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    words = cursor.execute(f"SELECT * FROM Words").fetchall()

    for word in words:
        try:
            cursor.execute('INSERT OR IGNORE INTO Trainings (user_id, word_id, successes, failures) VALUES ( ?, ?, ?, ? )',
                           (user_id, word[0], 0, 0))
        except:
            print(f"Trying to insert duplicate of {word[0]} for user {user_id}")
    connection.commit()
    cursor.close()
    connection.close()


def save_session_for_user(user_id, word_id):
    write_data('INSERT OR IGNORE INTO Sessions (user_id, word_id) VALUES ( ?, ? )', (user_id, word_id))


def write_data(query, data):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, data)
    connection.commit()
    cursor.close()
    connection.close()


def get_session_for_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    session = cursor.execute(f"SELECT * FROM Sessions WHERE user_id = {user_id}").fetchall()
    cursor.close()
    connection.close()
    #todo return session[0] if len(session) == 1 else raise Exception('I know Python!')
    return session[0]


def get_word(word_id):
    connection = get_connection()
    cursor = connection.cursor()
    word = cursor.execute(f"SELECT * FROM Words WHERE id = {word_id}").fetchall()
    cursor.close()
    connection.close()
    #todo return session[0] if len(session) == 1 else raise Exception('I know Python!')
    return word[0]


def delete_session_for_user(user_id):
    write_data(f"DELETE FROM Sessions WHERE user_id = {user_id}", ())
