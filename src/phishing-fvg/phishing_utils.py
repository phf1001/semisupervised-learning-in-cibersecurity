import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy as np
import re
import csv
from urllib.parse import urlparse
import json
import requests
from bs4 import BeautifulSoup
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

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


def get_available_proxies():
    """
    Returns directions included in proxies.json

    Returns
    -------
    list
        list containing Tor proxies.
    """

    f = open('proxies.json')
    data = json.load(f)
    f.close()
    return data
    

def get_proxy():
    """
    Returns
    -------
    dict
        dict containing http proxy
    """

    return get_available_proxies()[0]

def is_simple_php_file(name):
    """
    Checks if an string is a simple php
    file (no /).

    Returns
    -------
    bool
        True if it is, False if not.
    """

    return bool(re.match('[A-Za-z0-9_-]*\.php', name))


def is_absolute(url):
    """
    Checks if a url is absolute.

    Returns
    -------
    bool
        True if it is, False if not.
    """

    return bool(urlparse(url).netloc)


def is_relative_in_local(url):
    """
    Checks if a url is relative in the
    server.

    Returns
    -------
    bool
        True if it is, False if not.
    """

    if is_absolute(url):
        return False

    return url[0] == '/' or not '/' in url


def is_foreign(self_url, url):
    """
    Checks if a url is foreign to another.

    Returns
    -------
    bool
        True if it is, False if not.
    """

    return not is_empty(url) and not is_relative_in_local(url) and urlparse(self_url).netloc != urlparse(url).netloc
    

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

    try:
        return netloc[:netloc.rindex('.')]

    except:
        return netloc


def get_phishing_targets_set():
    """
    Returns a set containing some of the most
    common phishing targets.

    Returns
    -------
    set
        Set containing phishing targets.
    """

    with open('phishing_targets.csv') as f:
        reader = csv.reader(f)
        targets = list(reader)

    f.close()
    return set([target[0] for target in targets])


def is_empty(url):
    """
    Checks if a URL is empty.

    Returns
    -------
    bool
        True if it is, False if not.
    """

    return url == '' or url[0] == '#' or bool(re.match('[Jj]ava[Ss]cript::?void\(0\)', url))


def remove_stop_words(data):
    """
    Removes non functional words from a web.
    """

    stop_words = ( stopwords.words('english') + stopwords.words('spanish'))

    new_text = ''
    for w in data:
        if w not in stop_words and len(w) > 1:
            new_text = new_text + ' ' + w
    return new_text


def remove_punctuation(data):
    """
    Removes punctuation from a web.
    """

    symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~\n"
    for i in range(len(symbols)):
        data = np.char.replace(data, symbols[i], ' ')
        data = np.char.replace(data, "  ", " ")
    data = np.char.replace(data, ',', '')
    return data


def remove_apostrophe(data):
    """
    Deletes apostrophe from a website.
    """
    return np.char.replace(data, "'", "")


def preprocess(data):
    """
    Returns tokens of the words in a text
    once it has been processed.
    """

    data = data.split()
    data = np.char.lower(data)
    data = remove_punctuation(data)
    data = remove_apostrophe(data)
    data = remove_stop_words(data)

    return word_tokenize(str(data))


def get_popular_words(html, k=10):
    """
    Extracts a number of the most repeated
    words in a website.
    """

    cleaned = BeautifulSoup(html, "lxml").text
    tokens = preprocess(cleaned)
    counter = Counter(tokens)
    n_words = len(tokens)

    for token in np.unique(tokens):
    
        tf = counter[token]/n_words
        #df = doc_freq(token)
        #idf = np.log((N+1)/(df+1))
    
    #tf_idf[doc, token] = tf*idf
    return counter.most_common(k)


def get_number_foreign_hyperlinks(url, hyperlinks):
    """
    Returns the number of foreign hyperlinks

    Returns
    -------

    int
        number of foreign hyperlinks
    """

    n_foreigns = 0

    for h in hyperlinks:
        if is_foreign(url, h):
            n_foreigns += 1

    return n_foreigns


def get_number_empty_hyperlinks(hyperlinks):
    """
    Returns the number of empty hyperlinks

    Returns
    -------

    int
        number of empty hyperlinks
    """

    n_empty = 0

    for h in hyperlinks:
        if is_empty(h):
            n_empty += 1

    return n_empty


def get_number_errors(hyperlinks, headers, proxies):
    """
    Returns the number of errors in some
    hyperlinks.

    Returns
    -------

    int
        number of errors
    """

    n_errors = 0

    for h in hyperlinks:

        if not is_empty(h) and not is_relative_in_local(h):

            try:
                code = get_response_code(h, headers, proxies)
                if code == 404 or code == 403:
                    n_errors += 1
            
            except:
                pass

    return n_errors


def get_number_redirects(hyperlinks, headers, proxies):
    """
    Returns the number of redirections in some
    hyperlinks.

    Returns
    -------

    int
        number of redirections
    """

    n_redirects = 0

    for h in hyperlinks:

        if not is_empty(h) and not is_relative_in_local(h):

            try:
                code = get_response_code(h, headers, proxies)
                if code == 302 or code == 301:
                    n_redirects += 1
            
            except:
                pass

    return n_redirects


def get_response_code(url, headers, proxies):
    """
    Returns the status code of a request.

    Returns
    -------
    int
        status code

    """
    return requests.get(url, headers=headers, proxies=proxies, allow_redirects=False).status_code


def extract_url_href(tag):
    """
    Returns url included inside href atribute.

    Parameters
    ----------
    tag : str
        Tag containing the href atribute.

    Returns
    -------
    str
        extracted link (empty if none)

    """

    matches = re.findall('(?:href=")([^"]*)(?:")', str(tag))

    if len(matches) > 0:
        return matches[0]
    
    return ''


def get_meta(html):
    """
    Returns the content of a meta tag.
    """

    keywords = []
    found = re.findall('(?:<meta)([^>]*)(?:>)', html)

    for content in found:
        match = re.findall('(?:content=")([^"]*)(?:")', content)

        if len(match) > 0:
            keywords.append(match[0])

    return keywords


def get_title(html):
    """
    Returns the title of an html page.
    """
    matches = re.findall('(?:<title>)([^<]*)(?:</title>)', html)

    if len(matches) > 0:
        return matches[0]
    
    return ''


def find_hyperlinks(html):
    """
    Finds number of pages in a website extracting them
    from the src attribute and href attribute of anchor
    tags.
    """
    return ( re.findall('(?:src\b*=\b*")([^"]*)(?:")', html) + re.findall('(?:href\b*=\b*")([^"]*)(?:")', html) )


def get_bin_source_code(url, headers, proxies, fichero='html_dump'):
    """
    Extracts binary source code from webpage.
    """

    response = requests.get(url, headers=headers, proxies=proxies)

    if response.status_code != 400:
        with open(fichero, 'wb') as f:
            f.write(response.content)
            f.close()

    return response.content


def get_text_cleaned(html):
    """
    Returns a html text cleaned as a string.

    Returns
    --------

    str:
        string containing html cleaned.
    """

    raw = BeautifulSoup(html).get_text()
    tokens = nltk.word_tokenize(raw)

    htmlwords = ['https', 'http', 'display', 'button', 'hover',
                'color', 'background', 'height', 'none', 'target',
                'WebPage', 'reload', 'fieldset', 'padding', 'input',
                'select', 'textarea', 'html', 'form', 'cursor',
                'overflow', 'format', 'italic', 'normal', 'truetype',
                'before', 'name', 'label', 'float', 'title', 'arial', 'type',
                'block', 'audio', 'inline', 'canvas', 'margin', 'serif', 'menu',
                'woff', 'content', 'fixed', 'media', 'position', 'relative', 'hidden',
                'width', 'clear', 'body', 'standard', 'expandable', 'helvetica',
                'fullwidth', 'embed', 'expandfull', 'fullstandardwidth', 'left', 'middle',
                'iframe', 'rgba', 'selected', 'scroll', 'opacity',
                'center', 'false', 'right']

    text = ' '

    for w in tokens:
        if w.isalpha() and len(w) > 3 and w.lower() not in htmlwords:
            text += (' ' + w)
        
    return text


def get_tfidf_corpus(urls, headers, proxies):
    """
    Returns the corpus of a group of
    web pages.

    Returns
    --------

    array:
            array of texts
    """

    corpus = []

    for url in urls:

        try:
            html = get_bin_source_code(url, headers, proxies)
            html = html.decode("utf-8", errors='ignore')
            corpus.append(get_text_cleaned(html))

        except:
            pass

    return corpus



def get_tfidf(corpus):
    """
    Returns a tfidf model trained with the
    corpus.

    Returns
    --------
    TfidfVectorizer:
        object trained.
    """

    tfidf = TfidfVectorizer(stop_words=['english', 'spanish'])
    tfidf.fit_transform(corpus)
    return tfidf


def get_top_keywords(tfidf, text, n=10):
    """
    Returns top keywords from a text.

    Returns
    --------

    array
        array containing n keywords.
    """

    response = tfidf.transform([text])
    feature_names = tfidf.get_feature_names()
    feature_array = np.array(feature_names)
    tfidf_sorting = np.argsort(response.toarray()).flatten()[::-1]
    return feature_array[tfidf_sorting][:n]


def get_site_keywords(html, tfidf, n=10):
    """
    Returns a set of the most popular keywords in
    a website. Extracted from the title, meta 
    tag and text.
    """
    
    list = get_title(html).split(" ") + get_meta(html)
    words = ' '.join(list)
    set_one = set(preprocess(words))
    set_two = set(get_top_keywords(tfidf, html, n))

    return set_one.union(set_two)