import sqlite3


def get_connection():
    return sqlite3.connect('vocabulary-portuguese.sqlite')


def init_database():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Words
        (id INTEGER PRIMARY KEY, word TEXT, transcription TEXT, translation TEXT)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Trainings
        (id INTEGER PRIMARY KEY, word_id INTEGER, successes INTEGER, failures INTEGER, last_failure REAL,
        FOREIGN KEY(word_id) REFERENCES Words(id))''')
    cur.close()
    conn.close()


def create_new_word(word, transcription, translation):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT OR IGNORE INTO Words (word, transcription, translation) VALUES ( ?, ?, ? )',
                   (word, transcription, translation))
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

