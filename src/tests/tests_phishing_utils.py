#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   tests_phishing_utils.py
@Time    :   2023/03/30 20:55:06
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
"""

import unittest
import os
import sys
from html import unescape

src_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(src_path)
from phishing_fvg.phishing_utils import (
    translate_leet_to_letters,
    get_splitted_url,
    get_tlds_set,
    get_phishing_targets_set,
    remove_tld,
    is_empty,
    is_simple_php_file,
    is_absolute,
    is_foreign,
    is_in_local,
    find_data_URIs,
    get_title,
    get_number_errors,
    get_bin_source_code,
)


class phishingUtilsMethods(unittest.TestCase):
    """
    Tests for `phishing_utils.py
    Execute from parent directory
    """

    def test_translate_leet(self):
        """
        Test to check if the leet translator
        works correctly
        """
        phishing_words = ["l0g1n", "13urg05", "5h0pp1ng", "4maz0n", "m1crosoft"]
        real_words = ["login", "burgos", "shopping", "amazon", "microsoft"]

        for phish, real in zip(phishing_words, real_words):
            alternatives = translate_leet_to_letters(phish)
            self.assertTrue(real in alternatives)

    def test_split_url(self):
        """
        Test to check if the url splitter
        is working
        """
        urls = [
            "https://ubuvirtual.ubu.es/",
            "www.ubu-virtual.ubu.es/ruta/archivo.php",
        ]
        splitted_urls = [
            ["https", "ubuvirtual", "ubu", "es"],
            ["www", "ubu", "virtual", "ubu", "es", "ruta", "archivo", "php"],
        ]

        for input_test, output_test in zip(urls, splitted_urls):
            result = get_splitted_url(input_test)
            self.assertTrue(result == output_test)

    def test_tlds_set(self):
        """Checks if the tlds set is being created"""
        tlds = get_tlds_set()
        self.assertTrue(len(tlds) > 100)
        self.assertTrue(bool(tlds & {"com"}))
        self.assertTrue(bool(tlds & {"es"}))
        self.assertTrue(bool(tlds & {"edu"}))
        self.assertTrue(bool(tlds & {"fr"}))
        self.assertTrue(bool(tlds & {"org"}))

    def test_targets_set(self):
        """Tests if the phishing targets set is being created"""
        tlds = get_phishing_targets_set()
        self.assertTrue(bool(tlds & {"amazon"}))
        self.assertTrue(bool(tlds & {"dropbox"}))
        self.assertTrue(bool(tlds & {"azure"}))
        self.assertTrue(bool(tlds & {"linkedin"}))
        self.assertTrue(bool(tlds & {"correos"}))

    def test_remove_tld(self):
        """Checks if the tld is being removed correctly"""
        urls = [
            "ubuvirtual.ubu.es.org.uk",
            "ubuvirtual.ubu.es.org",
            "ubuvirtual.ubu.es",
        ]
        without_tlds = [
            "ubuvirtual.ubu.es.org",
            "ubuvirtual.ubu.es",
            "ubuvirtual.ubu",
        ]

        for input_test, output_test in zip(urls, without_tlds):
            result = remove_tld(input_test)
            self.assertTrue(result == output_test)

    def test_empty_content(self):
        """
        Checks if the empty content is being detected
        correctly in a HTML string.
        """
        empty = ["#", "javascript:void(0)", "", "#content"]
        not_empty = ["something", "/unexpected"]

        for input_test in empty:
            self.assertTrue(is_empty(input_test))

        for input_test in not_empty:
            self.assertFalse(is_empty(input_test))

    def test_simple_php_file(self):
        """
        Checks if the simple php file is being detected
        (just the name and extension)
        """
        simple = ["index.php", "login.php", "mail.php"]
        not_simple = ["/index.php", "something.something.php"]

        for input_test in simple:
            self.assertTrue(is_simple_php_file(input_test))

        for input_test in not_simple:
            self.assertFalse(is_simple_php_file(input_test))

    def test_domains(self):
        """
        Checks if the categories of domains are being
        labeled properly
        """
        base = "https://ubuvirtual.ubu.es/"
        absolute = [
            "https://pwr.edu.pl/",
            "https://www.uc3m.es/Inicio",
            "https://estudios.uoc.edu/es/estudiar-online",
        ]
        relative = [
            "/mail.php",
            "/image/ruta/inventada.jpg",
            "hola.html",
            "otra/ruta/.png",
            "../otra/ruta/mas.html",
        ]

        for input_test in absolute:
            self.assertTrue(is_absolute(input_test))
            self.assertTrue(is_foreign(base, input_test))
            self.assertFalse(is_in_local(input_test))

        for input_test in relative:
            self.assertFalse(is_absolute(input_test))
            self.assertTrue(is_in_local(input_test))

    def test_data_URIs(self):
        """
        Checks if the data URIs are being
        found correctly
        """
        input_test = '<img src="data:,Hello%2C%20World!">'
        input_test += (
            " <doc src='data:text/plain;base64,SGVsbG8sIFdvcmxkIQ%3D%3D'>"
        )
        input_test += "<img src=data:text/html,%3Ch1%Hello%2C%20World!%3C%h1> "
        input_test += "  data:text/html,<script>alert('hi');</script>  "
        input_test += "<img src=data text/html,%3Ch1Hello%2C%20World!%3C%h1%3> "
        input_test += '<img src ="/ruta/inventada.png">'

        self.assertTrue(len(find_data_URIs(input_test)) == 4)
        self.assertTrue(len(find_data_URIs("No hay URIs")) == 0)

    def test_title(self):
        """
        Checks if the title is being extracted
        correctly from a HTML file
        """
        content_one = get_bin_source_code("https://ubuvirtual.ubu.es/", {}, {})
        content_two = get_bin_source_code(
            "https://secretariavirtual.ubu.es/", {}, {}
        )
        inputs = [
            unescape(content_one.decode("utf-8", errors="ignore")),
            unescape(content_two.decode("utf-8", errors="ignore")),
        ]

        outputs = [
            "UBUVirtual - Aula Virtual de la Universidad de Burgos",
            "Identificacin",
        ]

        for input_test, output_test in zip(inputs, outputs):
            result = get_title(input_test)
            self.assertTrue(result == output_test)

    def test_get_number_errors(self):
        self.assertTrue(
            get_number_errors(
                [
                    "https://github.com/phf1001/semisupervised-recommendation-atk-detection"
                ],
                {},
                {},
            )
            == 1
        )


if __name__ == "__main__":
    """This is executed when run from the command line"""
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
