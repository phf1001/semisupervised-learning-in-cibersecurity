#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   phishing_vector_generator.py
@Time    :   2023/03/30 21:02:32
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
"""

import numpy as np
import re
from urllib.parse import urlparse
import os
import sys
from tld import get_tld
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from html import unescape

src_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(src_path)
from phishing_fvg.user_browsing import UserBrowsing
from phishing_fvg.phishing_utils import (
    get_bin_source_code,
    find_hyperlinks_tags,
    get_suspicious_keywords,
    get_splitted_url,
    translate_leet_to_letters,
    get_splitted_url_keep_dots,
    get_tlds_set,
    get_phishing_targets_set,
    find_data_URIs,
    is_empty,
    is_simple_php_file,
    is_foreign,
    get_number_foreign_hyperlinks,
    get_number_empty_hyperlinks,
    get_number_errors,
    get_number_redirects,
    extract_url_href,
    remove_punctuation,
    get_site_keywords,
)


class PhishingFVG:
    """
    Class that extracts the feature vector from a given URL.

    Author: @patricia-hernando
    """

    def __init__(self, url, tfidf, get_proxy_from_file=True, proxy=None):
        self.url = url
        parsed = urlparse(url)
        self.base = parsed.netloc
        self.path = parsed.path

        self.fv = np.array([-1 for _ in range(19)])

        self.user = UserBrowsing(
            get_proxy_from_file=get_proxy_from_file, proxy=proxy
        )

        response_content = get_bin_source_code(
            self.url,
            self.user.get_simple_user_header_agent(),
            self.user.proxies,
        )

        content = response_content.decode("utf-8", errors="ignore")
        self.html = unescape(content)
        self.soup = BeautifulSoup(response_content, "lxml")

        self.hyperlinks = find_hyperlinks_tags(self.soup)
        self.tfidf = tfidf

        self.extra_information = {"f{}".format(i): None for i in range(1, 20)}

    def set_feature_vector(self):
        """Sets the feature vector for the URL."""
        self.set_f1()
        self.set_f2()
        self.set_f3()
        self.set_f4()
        self.set_f5()
        self.set_f6()
        self.set_f7()
        self.set_f8()
        self.set_f9()
        self.set_f10_f11()
        self.set_f12()
        self.set_f13()
        self.set_f14()
        self.set_f15()
        self.set_f16()
        self.set_f17()
        self.set_f18()
        self.set_f19()

    def set_f1(self):
        """
        Sets F1.
        F1 = 1, if dots in url >= 4
        F1 = 0, otherwise
        """
        n_dots = self.url.count(".")
        self.extra_information["f1"] = n_dots

        if n_dots >= 4:
            self.fv[0] = 1

        else:
            self.fv[0] = 0

    def set_f2(self):
        """
        Sets F2.
        F2 = 1, if URL contains '@' or '-' symbols
        F2 = 0, otherwise
        """
        at_found = "@" in self.url
        minus_found = "-" in self.url

        found_characters = ""

        if at_found and minus_found:
            found_characters += "@ y -"
        elif at_found:
            found_characters += "@"
        elif minus_found:
            found_characters += "-"
        else:
            found_characters += ""

        self.extra_information["f2"] = found_characters

        if at_found or minus_found:
            self.fv[1] = 1

        else:
            self.fv[1] = 0

    def set_f3(self):
        """
        Sets F3.
        F3 = 1, if URL length >= 74
        F3 = 0, otherwise
        """
        self.extra_information["f3"] = len(self.url)

        if len(self.url) >= 74:
            self.fv[2] = 1

        else:
            self.fv[2] = 0

    def set_f4(self):
        """
        Sets F4.
        F4 = 1, if URL contains any suspicious word
        F4 = 0, otherwise
        """
        suspicious_words = get_suspicious_keywords()

        for word in suspicious_words:
            if word in self.url:
                self.fv[3] = 1
                self.extra_information["f4"] = word
                return

        splitted_url = get_splitted_url(self.url)

        for word in splitted_url:
            leet_translation = translate_leet_to_letters(
                word
            )  # Decisión propia

            if bool(suspicious_words & leet_translation):
                self.fv[3] = 1
                self.extra_information["f4"] = word
                return

        self.fv[3] = 0
        self.extra_information["f4"] = ""

    def set_f5(self):
        """
        Sets F5.
        F5 = 1, if tlds in URL > 1
        F5 = 0, otherwise
        """
        tld = get_tld(self.url, fix_protocol=True)
        base_without_tld = self.base[: -len(tld) - 1]
        rest = base_without_tld + self.path

        splitted_url = get_splitted_url_keep_dots(rest)
        tlds = get_tlds_set()
        tlds = {"." + tld for tld in tlds}

        extra_tlds_found = splitted_url & tlds

        if len(extra_tlds_found) >= 1:
            self.fv[4] = 1
            self.extra_information["f5"] = ", ".join(extra_tlds_found)

        else:
            self.fv[4] = 0
            self.extra_information["f5"] = ""

    def set_f6(self):
        """
        Sets F6.
        F6 = 1, if http count in URL > 1
        F6 = 0, otherwise
        """
        if len(re.findall("http", self.url)) > 1:
            self.fv[5] = 1
            self.extra_information["f6"] = "yes"

        else:
            self.fv[5] = 0
            self.extra_information["f6"] = "no"

    def set_f7(self):
        """
        Sets F7.
        F7 = 1, if brand in incorrect position (subdomains).
        F7 = 0, otherwise
        """
        remove_word = True
        targets = get_phishing_targets_set()

        lower_url = self.url.lower()
        parsed = urlparse(lower_url)
        path = parsed.path + parsed.query

        for target in targets:
            if target in path:  # or target in sub_domains
                self.fv[6] = 1
                self.extra_information["f7"] = target
                return

        # Extra checking - leet translation wherever except base
        # domain and tld but not exact word

        base = parsed.netloc
        tld = get_tld(lower_url, fix_protocol=True)
        without_tld = base[: -len(tld) - 1]

        if without_tld.count(".") > 0:
            sub_domains = without_tld[: without_tld.rindex(".")]

        elif without_tld.count("-") > 0:
            sub_domains = without_tld
            remove_word = False
        else:
            sub_domains = ""

        for word in get_splitted_url(path + sub_domains):
            leet_translation = translate_leet_to_letters(
                word
            )  # Decisión propia

            # If the original one does not have numbers it is removed
            if not re.search(r"\d", word) and remove_word:
                leet_translation -= {word}

            for fake in leet_translation:
                for target in targets:
                    if SequenceMatcher(None, fake, target).ratio() >= 0.8:
                        self.fv[6] = 1
                        self.extra_information["f7"] = target
                        return

        self.fv[6] = 0
        self.extra_information["f7"] = ""

    def set_f8(self):
        """
        Sets F8.
        F8 = 1, if data URI present in website.
        F8 = 0, otherwise
        """
        matches = find_data_URIs(self.html)

        if len(matches) > 0:
            self.fv[7] = 1
            self.extra_information["f8"] = len(matches)

        else:
            self.fv[7] = 0
            self.extra_information["f8"] = 0

    def set_f9(self):
        """
        Sets F9.
        F9 = 1, if action field is blank or javascript:void(0)
        F9 = 1, if action field is <name>.php
        F9 = 1, if action field contains foreign base domain
        F9 = 0, otherwise
        """
        forms_found = re.findall("<form[^>]+>", self.html)

        if len(forms_found) > 0:
            for _, form_found in enumerate(forms_found):
                action_content = re.findall(
                    '(?:action=")([^"]*)(?:")', form_found
                )

                if len(action_content) > 0:
                    if is_empty(action_content[0]):
                        self.fv[8] = 1
                        self.extra_information["f9"] = 1
                        return

                    if is_simple_php_file(action_content[0]):
                        self.fv[8] = 1
                        self.extra_information["f9"] = 2
                        return

                    if is_foreign(self.url, action_content[0]):
                        self.fv[8] = 1
                        self.extra_information["f9"] = 3
                        return

        self.fv[8] = 0
        self.extra_information["f9"] = 4

    def set_f10_f11(self):
        """
        Sets F10 and F11.

        F10 = number of hyperlinks in source code.

        F11 = 1, if no hyperlinks found in source.
        F11 = 0, otherwise
        """
        n_hyperlinks_found = len(self.hyperlinks)
        self.fv[9] = n_hyperlinks_found
        self.extra_information["f10"] = n_hyperlinks_found

        if n_hyperlinks_found == 0:
            self.fv[10] = 1
            self.extra_information["f11"] = "yes"

        else:
            self.fv[10] = 0
            self.extra_information["f11"] = "no"

    def set_f12(self):
        """
        Sets F12.

        ratio = |n_foreign_hyp| / |n_hyp|

        F12 = 1 if ratio > 0.5 and n_hyp > 0
        F12 = 0 otherwise
        """
        n_foreigns = get_number_foreign_hyperlinks(self.url, self.hyperlinks)
        self.extra_information["f12"] = n_foreigns

        if len(self.hyperlinks) == 0:
            self.fv[11] = 0  # Opino que debería ser 1
            return

        ratio = n_foreigns / len(self.hyperlinks)

        if ratio > 0.5:
            self.fv[11] = 1
        else:
            self.fv[11] = 0

    def set_f13(self):
        """
        Sets F13.

        ratio = |n_empty_hyp| / |n_hyp|

        F13 = 1 if ratio > 0.34 and n_hyp > 0
        F13 = 0 otherwise
        """
        n_empty = get_number_empty_hyperlinks(self.hyperlinks)
        self.extra_information["f13"] = n_empty

        if len(self.hyperlinks) == 0:
            self.fv[12] = 0  # Opino que debería ser 1
            return

        ratio = n_empty / len(self.hyperlinks)

        if ratio > 0.34:
            self.fv[12] = 1
        else:
            self.fv[12] = 0

    def set_f14(self):
        """
        Sets F14.

        ratio = |n_errors_hyp| / |n_hyp|

        F14 = 1 if ratio > 0.3 and n_hyp > 0
        F14 = 0 otherwise
        """
        n_errors = get_number_errors(
            self.hyperlinks,
            self.user.get_simple_user_header_agent(),
            self.user.proxies,
        )
        self.extra_information["f14"] = n_errors

        if len(self.hyperlinks) == 0:
            self.fv[13] = 0  # Opino que debería ser 1
            return

        ratio = n_errors / len(self.hyperlinks)

        if ratio > 0.3:
            self.fv[13] = 1
        else:
            self.fv[13] = 0

    def set_f15(self):
        """
        Sets F15.

        ratio = |n_redirects| / |n_hyp|

        F15 = 1 if ratio > 0.3 and n_hyp > 0
        F15 = 0 otherwise
        """
        n_redirects = get_number_redirects(
            self.hyperlinks,
            self.user.get_simple_user_header_agent(),
            self.user.proxies,
        )
        self.extra_information["f15"] = n_redirects

        if len(self.hyperlinks) == 0:
            self.fv[14] = 0  # Opino que debería ser 1
            return

        ratio = n_redirects / len(self.hyperlinks)

        if ratio > 0.3:
            self.fv[14] = 1
        else:
            self.fv[14] = 0

    def set_f16(self):
        """
        Sets F16.

        F16 = 1, if CSS file is external and contains foreign domain name
        F16 = 0, otherwise

        """
        external_csss = self.soup.findAll("link", rel="stylesheet")

        for css in external_csss:
            link = extract_url_href(css)

            if is_foreign(self.url, link):
                self.extra_information["f16"] = "yes"
                self.fv[15] = 1
                return

        self.fv[15] = 0
        self.extra_information["f16"] = "no"

    def set_f17(self):
        """
        Sets F17.
        F17 = 0 if copyright keyword matches base domain
        F17 = 1, otherwise
        """
        copyright_clues = [
            "©",
            "&#169",
            "& copy",
            "&copy",
            "copy",
            "copyright",
            "copyright",
            "all right reserved",
            "rights",
            "right",
        ]  # '@',

        for clue in copyright_clues:
            regex = "(?:{})([^<.>\"']*)(?:[<.>\"'])".format(clue)
            copy_contents = re.findall(regex, self.html)

            for copy_content in copy_contents:
                copy_content = remove_punctuation(copy_content).reshape(1)

                for content in copy_content[0].split():
                    # Avoid single letters or small strings
                    if len(content) > 2 and re.findall(
                        content.replace(",", ""), self.base, re.IGNORECASE
                    ):
                        self.fv[16] = 0
                        self.extra_information["f17"] = content
                        return

        self.fv[16] = 1
        self.extra_information["f17"] = ""

    def set_f18(self):
        """
        Set F18.
        F18 = 1 if no keyword matches domain name
        F18 = 0 Otherwise
        """
        keywords = get_site_keywords(self.html, self.tfidf, 15)

        for keyword in keywords:
            if len(keyword) >= 3 and re.findall(keyword, self.base):
                self.fv[17] = 0
                self.extra_information["f18"] = keyword
                return

        self.fv[17] = 1
        self.extra_information["f18"] = ""

    def set_f19(self):
        """
        Sets F19.
        F19 = 1, if foreign domain found in favicon link
        F19 = 0, otherwise
        """
        icons = self.soup.findAll("link", rel="icon")
        icons += self.soup.findAll("link", rel="shortcut icon")

        for icon in icons:
            link = extract_url_href(icon)

            if is_foreign(self.url, link):
                self.fv[18] = 1
                self.extra_information["f19"] = "yes"
                return

        self.fv[18] = 0
        self.extra_information["f19"] = "no"
