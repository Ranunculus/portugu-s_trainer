import sqlite3
import datetime


def get_connection():
    return sqlite3.connect('vocabulary-portuguese.sqlite')


def init_database():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Words
        (id INTEGER PRIMARY KEY, word TEXT, transcription TEXT, translation TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Trainings
        (id INTEGER PRIMARY KEY, word_id INTEGER, successes INTEGER, failures INTEGER, next_training_date REAL,
        FOREIGN KEY(word_id) REFERENCES Words(id))''')
    cur.close()
    conn.close()


def create_new_word(word, transcription, translation):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT OR IGNORE INTO Words (word, transcription, translation) VALUES ( ?, ?, ? )',
                   (word, transcription, translation))

    word_id = cursor.execute('SELECT id FROM Words WHERE word = (?)', (word,)).fetchall()
    cursor.execute('INSERT OR IGNORE INTO Trainings (word_id, successes, failures) VALUES ( ?, ?, ? )',
                   (word_id[0][0], 0, 0))
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


def list_words_for_training(words_amount):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        f"SELECT word_id FROM Trainings WHERE next_training_date IS NULL OR next_training_date < DATETIME('now','localtime') LIMIT {words_amount}")

    word_ids = cursor.fetchall()

    rows = []
    if len(word_ids) > 0:
        result = []
        for t in word_ids:
            result.append(t[0])
        join = ','.join(['?']*len(result))
        query = f"SELECT * FROM Words WHERE id IN ({join})"
        rows = cursor.execute(query, result).fetchall()

    cursor.close()
    connection.close()
    return rows


def save_training_result(word_id, ratio):
    connection = get_connection()
    cursor = connection.cursor()
    if ratio == 100:
        cursor.execute('UPDATE Trainings SET successes = successes + 1, next_training_date = ? WHERE word_id = (?)', ((datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%B %d, %Y %I:%M%p"), word_id,))
    else:
        cursor.execute('UPDATE Trainings SET failures = failures + 1, next_training_date = ? WHERE word_id = ?',
                       (datetime.now().strftime("%B %d, %Y %I:%M%p"), word_id))

    connection.commit()
    cursor.close()
    connection.close()
