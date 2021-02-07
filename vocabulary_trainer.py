from portugués_trainer import database_operations as database
from fuzzywuzzy import fuzz as fuzzy_search


def process_input(how_many_words):
    words_for_training = database.list_words_for_training(how_many_words)

    if len(words_for_training) == 0:
        print("You've already trained all of the words for today. Good job, rest for now)")
    # todo SM2
    for word in words_for_training:
        print(word[3])
        user_variant = input("Translate it:")
        ratio = fuzzy_search.ratio(word[1], user_variant)
        if ratio == 100:
            print("Good job!")
        if ratio < 100:
            print(f"Correct is: {word[1]}")

        database.save_training_result(word[0], ratio)


def train(how_many_words):
    process_input(how_many_words)
