import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from num2words import num2words
import numpy as np
import re
import csv

def turn_lower_case(text):
    return np.char.lower(text)

def remove_stop_words(data):

    stop_words = ( stopwords.words('english') + stopwords.words('spanish'))

    new_text = ''
    for w in data:
        if w not in stop_words and len(w) > 1:
            new_text = new_text + ' ' + w
    return new_text

def remove_punctuation(data):
    symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~\n"
    for i in range(len(symbols)):
        data = np.char.replace(data, symbols[i], ' ')
        data = np.char.replace(data, "  ", " ")
    data = np.char.replace(data, ',', '')
    return data

def remove_apostrophe(data):
    return np.char.replace(data, "'", "")

def stemming(data):
    stemmer= PorterStemmer()
    
    tokens = word_tokenize(str(data))
    new_text = ""
    for w in tokens:
        new_text = new_text + " " + stemmer.stem(w)
    return new_text

def convert_numbers(data):
    tokens = word_tokenize(str(data))
    new_text = ""
    for w in tokens:
        try:
            w = num2words(int(w))
        except:
            a = 0
        new_text = new_text + " " + w
    new_text = np.char.replace(new_text, "-", " ")
    return new_text

def preprocess(data):

    data = data.split()
    data = turn_lower_case(data)
    data = remove_punctuation(data)
    data = remove_apostrophe(data)
    data = remove_stop_words(data)

    return word_tokenize(str(data))


def translate_leet_to_letters(word):
    """
    Returns a set containing possible alternatives
    to the original word if it is translated from
    leet.

    Returns
    -------
    set
        Set containing alternatives + original,
        all of them in lower case.
    """

    word_original = str(word)
    word_lower = word.lower()
    word_upper = word.upper()

    full_map = dictionary_leetspeak()

    for key, value in full_map.items():

        for substitute in value:

            if substitute in word:
                word_original = word_original.replace(substitute, key)

            if substitute in word_lower:
                word_lower = word_lower.replace(substitute, key)
            
            if substitute in word_upper:
                word_upper = word_upper.replace(substitute, key)

    return set((word, word_original.lower(), word_lower.lower(), word_upper.lower()))


def dictionary_leetspeak():
    """
    Returns a Letter-to-Leet dictionary.

    Returns
    -------
    dict
        Dictionary containing common substitutions
    """

    return {
        "a": ["4", "@", "/-\\", "^"],
        "b": ["I3", "8", "13", "|3"],
        "c": ["[", "{", "<", "("],
        "d": [")", "|)", "[)", "|>"],
        "e": ["3", "[-"],
        "f": ["|=", "|#", "/="],
        "g": ["&", "6", "(_+]", "9", "C-"],
        "h": ["#", "/-/", "[-]", "]-[", ")-(", "(-)", ":-:", "|-|", "}{"],
        "i": ["1", "[]", "!", "|", "]["],
        "j": [",_|", "_|", "._|", "._]", ",_]", "]"],
        "k": [">|", "|<", "/<", "1<", "|c", "|(", "|{"],
        "l": ["1", "7", "|_", "|"],
        "m": ["/\\/\\", "/V\\", "JVI", "[V]", "[]V[]", "|\\/|", "^^"],
        "n": ["^/", "|\\|", "/\\/", "[\]", "<\\>", "{\\}", "|V", "/V"],
        "o": ["0", "Q", "()", "oh", "[]"],
        "p": ["|*", "|o", "?", "|^", "[]D"],
        "q": ["(_,)", "()_", "2", "O_"],
        "r": ["12", "|`", "|~", "|?", "/2", "|^", "Iz", "|9"],
        "s": ["$", "5", "z", "ehs", "es"],
        "t": ["7", "+", "-|-", "']['", '"|"', "~|~"],
        "u": ["|_|", "(_)", "V", "L|"],
        "v": ["\\/", "|/", "\\|"],
        "w": ["\\/\\/", "VV", "\\N", "'//", "\\\\'", "\\^/", "\\X/"],
        "x": ["><", ">|<", "}{"],
        "y": ["j", "`/", "\\|/", "\\//"],
        "z": ["2", "7_", "-/_", "%", ">_", "~/_", "-\_", "-|_"],
    }
    

def get_splitted_url(url):
    """
    Returns an array containing all words in lower
    case in a url once it has been splitted.

    Returns
    -------
    array
        Array containing (lower) words in url

    """

    url = url.lower()
    url = re.split(':|/|\.| |\-', url)

    return [x for x in url if x != '']


def get_suspicious_keywords():
    """
    Returns a set containing typical phishing
    keywords.

    Returns
    -------
    set
        Set containing phishing keywords.
    """

    return set(('security', 'login', 'signin', 'sign', 'bank', 'account', 'update', 'include', 'webs', 'online'))


def get_tlds_set():
    """
    Returns a set containing 150 most common
    TLDs reported by Google.

    Returns
    -------
    set
        Set containing 150 TLDs.
    """

    with open('150_tlds.csv') as f:
        reader = csv.reader(f)
        tlds = list(reader)

    f.close()
    return set([tld[0] for tld in tlds])


def remove_tld(netloc):
    """
    Removes tld from a string.

    Parameters
    ----------
    netloc:
        string containing the net location (without
        protocols or paths)

    Returns
    -------
    str
        netloc without tld
    """

    return netloc[:netloc.rindex('.')]