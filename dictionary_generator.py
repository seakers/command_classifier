import json
import re


def create_dictionary(dictionary_file):
    dictionary = {}

    for line in open(dictionary_file):
        # If a line contains "(see ...)" then the homophones will be listed elsewhere.
        if "(see " in line:
            continue

        word_strings = [word.strip() for word in line.split(",")]

        words = []
        plural_words = []
        for word_string in word_strings:
            matches = re.findall("([^( ]+) ?(\(-(.+?)\))?", word_string)

            if not matches:
                continue

            word = matches[0][0]
            plural_word = matches[0][2]

            if plural_word:
                plural_words.append(word + plural_word)

            words.append(word)

        for word in words:
            dictionary[word.lower()] = [x for x in words if x is not word]
        for plural_word in plural_words:
            dictionary[plural_word.lower()] = [x for x in plural_words if x is not plural_word]

    return dictionary


def main():
    # create the dictionary file
    dictionary_file = 'homophones.txt'
    dictionary = create_dictionary(dictionary_file)
    print(json.dumps(dictionary))


main()
