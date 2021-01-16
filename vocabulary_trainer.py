from portugués_trainer import database_operations as database
from portugués_trainer import vocabulary_creator as creator


def main_menu():
    process_main_option(init_input())


def init_input():
    print('What would you like to do: ')
    print('Enter:')
    print('1 to train (Press Enter for this option)')
    print('2 to add new word')
    print('3 list all words')

    print('0 to exit')
    return input('Choose: ')


def process_main_option(option):
    if option == '1' or option == '':
        print('Under construction\n')
        main_menu()
        # how_many_words = input('How many words? (Enter for 10)')
        # print(10 if (how_many_words == '' or type(how_many_words) != int) else how_many_words)
        # todo train(10 if (how_many_words == '' or type(how_many_words) != int) else how_many_words)
    elif option == '2':
        creator.create_word_from_input()
    elif option == '3':
        for word in database.list_all():
            print(word)
        main_menu()
    elif option == '0':
        exit()
    else:
        print("Ha-ha, nice try")
        process_main_option(init_input())


if __name__ == "__main__":
    database.init_database()
    main_menu()
