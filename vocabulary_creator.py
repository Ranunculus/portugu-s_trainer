from portugués_trainer import database_operations as database
from portugués_trainer import vocabulary_trainer as trainer


def is_word(what_to_do):
    return what_to_do == 'w' or what_to_do == 'W'


def is_word_or_default(what_to_do):
    return what_to_do == '' or is_word(what_to_do)


def is_return(what_to_do):
    return what_to_do == 'r' or what_to_do == 'R'


def is_return_or_default(what_to_do):
    return what_to_do == '' or is_return(what_to_do)


def process_input(word, transcription, translation):
    check_result = input(f"Is everything correct? (Y/n) : {word} - {transcription} - {translation}")

    if check_result == 'Y' or check_result == 'y' or check_result == '':
        database.create_new_word(word, transcription, translation)
        what_to_do = input("Return to main menu, add new word or get the hell out of here? (r/W/g)")
        if is_return(what_to_do):
            trainer.main_menu()
        elif is_word_or_default(what_to_do):
            create_word_from_input()
        else:
            exit()
    else:
        correct_or_exit_to_main = input('Would you like to correct? (Y/n) :')
        if correct_or_exit_to_main == 'Y' or correct_or_exit_to_main == 'y' or correct_or_exit_to_main == '':
            print("What is wrong?")
            print("Enter:")
            print("w - word")
            print("tr - transcription")
            print("tl - translation")
            what_to_correct = input("Which one to correct? (w/tr/tl):")
            if what_to_correct == 'w':
                word = input('Enter word: ')
            elif what_to_correct == 'tr':
                transcription = input('Enter transcription: ')
            elif what_to_correct == 'tl':
                translation = input('Enter translation: ')
            else:
                print("Nice try :)")

            process_input(word, transcription, translation)
        else:
            what_to_do = input("Return to main menu, try with this word again or get the hell out of here? (R/w/g)")
            if is_return_or_default(what_to_do):
                trainer.main_menu()
            elif is_word(what_to_do):
                process_input(word, transcription, translation)
            else:
                exit()


def create_word_from_input():
    word = input('Enter word: ')
    transcription = input('Enter transcription: ')
    translation = input('Enter translation: ')
    process_input(word, transcription, translation)
