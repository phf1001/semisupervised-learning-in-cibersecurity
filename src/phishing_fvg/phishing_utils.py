import nltk
# nltk.download('stopwords')
# nltk.download('punkt')
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
import os
import pandas as pd


def get_data_path():
    """
    Returns data directory absolute path.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


def get_fv_path():
    """
    Returns fv directory absolute path.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'fv'))


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

    return {word, word_original.lower(), word_lower.lower(), word_upper.lower()}


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


def get_splitted_url_keep_dots(url):
    """
    Returns an array containing all words in lower
    case in a url once it has been splitted.

    Keeps dots.

    Returns
    -------
    set
        set containing (lower) words in url

    """
    url = url.lower()
    url = url.replace(".", " .")
    url = re.split(':|/| |\-', url)

    return set([x for x in url if x != ''])


def get_suspicious_keywords():
    """
    Returns a set containing typical phishing
    keywords.

    Returns
    -------
    set
        Set containing phishing keywords.
    """
    return {'security', 'login', 'signin', 'sign', 'bank', 'account', 'update', 'include', 'webs', 'online'}


def get_available_proxies():
    """
    Returns directions included in proxies.json

    Returns
    -------
    list
        list containing Tor proxies.
    """
    with open(get_data_path() + os.sep + 'proxies.json') as f:
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


def is_in_local(url):
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

    return url[:3] == '../' or url[0] == '/' or bool(re.match('[^.]+\.[A-Za-z]+', url))


def is_foreign(self_url, url):
    """
    Checks if a url is foreign to another.

    Returns
    -------
    bool
        True if it is, False if not.
    """
    return not is_empty(url) and not is_in_local(url) and urlparse(self_url).netloc != urlparse(url).netloc


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

    except ValueError:
        return netloc


def is_empty(url):
    """
    Checks if a URL is empty.

    Returns
    -------
    bool
        True if it is, False if not.
    """
    return url == '' or url[0] == '#' or bool(re.match('[Jj]ava[Ss]cript::?void\(0\)', url))


def find_data_URIs(html):
    """
    Finds data URIs in a web.

    Syntax: data:[<mime type>][;charset=<charset>][;base64],<encoded data>
    """
    matches = re.findall(
        'data:(?:[^;,]+)?(?:;charset=[^;,]*)?(?:;base64)?,[^)"\';>]+[^)"\';>]', html)

    return matches


def remove_stop_words(data):
    """Removes non functional words from a web."""
    stop_words = (stopwords.words('english') + stopwords.words('spanish'))

    new_text = ''
    for w in data:
        if w not in stop_words and len(w) > 1:
            new_text = new_text + ' ' + w
    return new_text


def remove_punctuation(data):
    """Removes punctuation from a web."""
    symbols = "!\"#$%&()*+-./:;\\<=>?@[]^_`{|}~\n"
    for symbol in symbols:
        data = np.char.replace(data, symbol, ' ')
        data = np.char.replace(data, "  ", " ")
    data = np.char.replace(data, ',', '')
    return data


def remove_apostrophe(data):
    """Deletes apostrophe from a website."""
    return np.char.replace(data, "'", "")


def preprocess(data):
    """
    Returns tokens of the words in a text
    once it has been processed.
    """

    try:
        data = data.split()
        data = np.char.lower(data)
        data = remove_punctuation(data)
        data = remove_apostrophe(data)
        data = remove_stop_words(data)
        return word_tokenize(str(data))

    except TypeError:
        return data


def get_popular_words(html, k=10):
    """
    Extracts a number of the most repeated
    words in a website.
    """
    cleaned = BeautifulSoup(html, "lxml").text
    tokens = preprocess(cleaned)
    counter = Counter(tokens)
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

        if not is_empty(h) and not is_in_local(h):

            try:
                code = get_response_code(h, headers, proxies)
                if code in (404, 403):
                    n_errors += 1

            except requests.exceptions.RequestException:
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

        if not is_empty(h) and not is_in_local(h):

            try:
                code = get_response_code(h, headers, proxies)
                if code in (301, 302):
                    n_redirects += 1

            except requests.exceptions.RequestException:
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
    return requests.get(url, headers=headers, proxies=proxies, allow_redirects=False, timeout=15).status_code


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
    """Returns the content of a meta tag."""
    keywords = []
    found = re.findall('(?:<meta)([^>]*)(?:>)', html)

    for content in found:

        if 'description' in content or 'keywords' in content or 'author' in content or 'copyright' in content:
            match = re.findall('(?:content=")([^"]*)(?:")', content)

            if len(match) > 0:
                keywords.append(match[0])

    return keywords


def get_title(html):
    """Returns the title of an html page."""
    matches = re.findall('(?:<title>)([^<]*)(?:</title>)', html)

    if len(matches) > 0:
        return matches[0]

    return ' '


def find_hyperlinks(html):
    """
    Finds number of pages in a website extracting them
    from the src attribute and href attribute.
    """
    links_one = re.findall('(?:src\b*=\b*(?:"|\'))([^"\']*)(?:"|\')', html)
    links_two = re.findall('(?:href\b*=\b*(?:"|\'))([^"\']*)(?:"|\')', html)
    return links_one + links_two


def find_hyperlinks_tags(soup):
    """
    Finds number of pages in a website extracting them
    from the src attribute and href attribute of given
    tags (paper).
    """
    links = []
    tags = ['img', 'script', 'frame', 'input', 'link']

    for tag in tags:
        links += [html_tag['src'] for html_tag in soup.find_all(tag, src=True)]

    links += [html_tag['href'] for html_tag in soup.find_all('a', href=True)]

    return links


def get_bin_source_code(url, headers, proxies, fichero=get_data_path() + os.sep + 'html_dump'):
    """Extracts binary source code from webpage."""
    response = requests.get(url, headers=headers, proxies=proxies, timeout=15)

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
    raw = BeautifulSoup(html, features='lxml').get_text(" ")
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
                 'center', 'false', 'right', 'div', 'page', 'data']

    text = ' '

    for w in tokens:
        if w.isalpha() and w.lower() not in htmlwords:
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

        except requests.exceptions.RequestException:
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
    feature_names = tfidf.get_feature_names_out()
    feature_array = np.array(feature_names)
    tfidf_sorting = np.argsort(response.toarray()).flatten()[::-1]
    return feature_array[tfidf_sorting][:n]


def get_site_keywords(html, tfidf, n=10):
    """
    Returns a set of the most popular keywords in
    a website. Extracted from the title, meta 
    tag and text.
    """
    list_words = get_title(html).split(" ") + get_meta(html)
    words = ' '.join(list_words)
    set_one = set(preprocess(words))
    set_two = set(get_top_keywords(tfidf, get_text_cleaned(html), n))

    return set_one.union(set_two)


def get_csv_data(file):
    """
    Returns a set with the content of a csv

    Returns
    -------
    set
        Set containing legitimate domains.
    """
    if '.csv' not in file:
        return 'Invalid file'

    with open(file) as f:
        reader = csv.reader(f)
        data = list(reader)

    f.close()
    return [d[0] for d in data if len(d) > 0]


def get_phishing_targets_set():
    """
    Returns a set containing some of the most
    common phishing targets.

    Returns
    -------
    set
        Set containing phishing targets.
    """
    return set(get_csv_data(get_data_path() + os.sep + 'phishing_targets.csv'))


def get_tlds_set():
    """
    Returns a set containing 150 most common
    TLDs reported by Google.

    Returns
    -------
    set
        Set containing 150 TLDs.
    """
    return set(get_csv_data(get_data_path() + os.sep + '150_tlds.csv'))


def get_alexa_sites(n=-1):
    """
    Returns a set containing the number of desired
    Alexa domains.

    Returns
    -------
    set
        Set containing sites from alexa top
    """
    data = get_csv_data(get_data_path() + os.sep + 'alexa_filtered.csv')

    if n == -1 or len(data) < n:
        return set(data)

    return set(data[:n])


def get_payment_gateways():
    """
    Returns a set containing some of the most
    common payment gateways

    Returns
    -------
    set
        Set containing payment gateways.
    """
    return set(get_csv_data(get_data_path() + os.sep + 'payment_gateways.csv'))


def get_banking_sites():
    """
    Returns a set containing some of the most
    common banking websites

    Returns
    -------
    set
        Set containing banking sites
    """
    return set(get_csv_data(get_data_path() + os.sep + 'banking_sites.csv'))


def get_legitimate_urls():
    """
    Returns a set containing a dataset of
    legitimate websites.

    Returns
    -------
    set
        Set containing legitimate domains.
    """
    set_one = get_alexa_sites()
    set_two = get_payment_gateways()
    set_three = get_banking_sites()

    return set_one.union(set_two).union(set_three)


def get_open_fish_urls():
    """
    Returns a set containing phishing
    sites extracted from open fish.

    Returns
    -------
    set
        Set containing phishing domains.
    """
    request = requests.get('https://openphish.com/feed.txt',
                           headers={
                               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
                           ).content

    list_s = request.decode("utf-8", errors='ignore').split("\n")
    return set(list_s)


def get_phish_tank_urls_json(n=2000, proxy=None):
    """
    Returns a set containing phishing
    sites extracted from phish tank.

    Returns
    -------
    set
        Set containing phishing domains.
    """
    try:

        request = requests.get('http://data.phishtank.com/data/online-valid.json',
                               headers={'User-Agent': 'phishtank/patrick'},
                               allow_redirects=True,
                               proxies=proxy)

        y = request.content.decode("utf-8", errors='ignore')
        json_content = json.loads(y)
        urls = [dictionary['url'].replace("\\", "")
                for dictionary in json_content]

        if len(urls) < n:
            return set(urls)

        return set(urls[:n])

    except (requests.exceptions.RequestException, json.JSONDecodeError):
        return set()


def get_phish_tank_urls_csv(n=2000):
    """
    Returns a set containing phishing
    sites extracted from phish tank.

    Returns
    -------
    set
        Set containing phishing domains.
    """
    try:

        request = requests.get('http://data.phishtank.com/data/online-valid.csv',
                               headers={'User-Agent': 'phishtank/patrick'},
                               allow_redirects=True)

        csv_reader = csv.reader(request.text.splitlines(), delimiter=',')
        content = list(csv_reader)
        df = pd.DataFrame(content[1:], columns=content[0])
        urls = df['url'].to_list()

        if len(urls) < n:
            return set(urls)

        return set(urls[:n])

    except requests.exceptions.RequestException:
        return set()
