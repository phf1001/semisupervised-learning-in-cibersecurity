import unittest
from phishing_vector_generator import PHISH_FVG
from phishing_utils import *
import os
import sys
src_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.append(src_path)

class RealFV(unittest.TestCase):
    
    def setUp(self):
        self.ph_entity = PHISH_FVG('https://ubuvirtual.ubu.es/')

    def test_proxy_working(self):

        ip_one = requests.get('http://ipinfo.io/ip', proxies = self.ph_entity.user.proxies).text
        ip_two = requests.get('http://ipinfo.io/ip').texts
        self.assertTrue(ip_one != ip_two)
        

class phishingUtilsMethods(unittest.TestCase):

    def test_translate_leet(self):

        phishing_words = ['l0g1n', '13urg05', '5h0pp1ng', '4maz0n', 'm1crosoft']
        real_words = ['login', 'burgos', 'shopping', 'amazon', 'microsoft']

        for phish, real in zip(phishing_words, real_words):
            alternatives = translate_leet_to_letters(phish)
            self.assertTrue(real in alternatives)

    
    def test_split_url(self):
        urls = ['https://ubuvirtual.ubu.es/', 'www.ubu-virtual.ubu.es/ruta/archivo.php']
        splitted_urls = [['https', 'ubuvirtual', 'ubu', 'es'], ['www', 'ubu', 'virtual', 'ubu', 'es', 'ruta', 'archivo', 'php']]

        for input_test, output_test in zip(urls, splitted_urls):
            result = get_splitted_url(input_test)
            self.assertTrue(result == output_test)


    def test_tlds_set(self):
        
        tlds = get_tlds_set()
        self.assertTrue(len(tlds) == 150)
        self.assertTrue(bool(tlds & {'com'}))
        self.assertTrue(bool(tlds & {'es'}))
        self.assertTrue(bool(tlds & {'edu'}))
        self.assertTrue(bool(tlds & {'fr'}))
        self.assertTrue(bool(tlds & {'org'}))


    def test_targets_set(self):
        
        tlds = get_phishing_targets_set()
        self.assertTrue(bool(tlds & {'amazon'}))
        self.assertTrue(bool(tlds & {'dropbox'}))
        self.assertTrue(bool(tlds & {'azure'}))
        self.assertTrue(bool(tlds & {'linkedin'}))
        self.assertTrue(bool(tlds & {'correos'}))


    def test_remove_tld(self):
        urls = ['ubuvirtual.ubu.es.org.uk', 'ubuvirtual.ubu.es.org', 'ubuvirtual.ubu.es']
        without_tlds = ['ubuvirtual.ubu.es.org', 'ubuvirtual.ubu.es', 'ubuvirtual.ubu']

        for input_test, output_test in zip(urls, without_tlds):
            result = remove_tld(input_test)
            self.assertTrue(result == output_test)


    def test_empty_content(self):
        
        empty = ['#', 'javascript:void(0)', '']
        not_empty = ['something', '/unexpected']

        for input_test in empty:
            self.assertTrue(is_empty(input_test))

        for input_test in not_empty:
            self.assertFalse(is_empty(input_test))


    def test_simple_php_file(self):
        
        simple = ['index.php', 'login.php', 'mail.php']
        not_simple = ['/index.php', 'something.something.php']

        for input_test in simple:
            self.assertTrue(is_simple_php_file(input_test))

        for input_test in not_simple:
            self.assertFalse(is_simple_php_file(input_test))


    def test_domains(self):
        
        base = 'https://ubuvirtual.ubu.es/'
        absolute = ['https://pwr.edu.pl/', 'https://www.uc3m.es/Inicio', 'https://estudios.uoc.edu/es/estudiar-online']
        relative = ['/mail.php', '/image/ruta/inventada.jpg', 'hola.html']

        for input_test in absolute:
            self.assertTrue(is_absolute(input_test))
            self.assertTrue(is_foreign(base, input_test))

        for input_test in relative:
            self.assertFalse(is_absolute(input_test))
            self.assertTrue(is_relative_in_local(input_test))

        
    def test_title(self):
        inputs = ['https://ubuvirtual.ubu.es/', 'https://secretariavirtual.ubu.es/']
        outputs = ['UBUVirtual - Aula Virtual de la Universidad de Burgos', 'Identificación']

        for input_test, output_test in zip(inputs, outputs):
            result = get_title(input_test)
            self.assertTrue(result == output_test)


    def test_title(self):
        inputs = ['https://ubuvirtual.ubu.es/', 'https://secretariavirtual.ubu.es/']
        outputs = ['UBUVirtual - Aula Virtual de la Universidad de Burgos', 'Identificación']

        for input_test, output_test in zip(inputs, outputs):
            result = get_title(input_test)
            self.assertTrue(result == output_test)


    def test_title(self):

        inputs = [get_bin_source_code('https://ubuvirtual.ubu.es/', {}, {}).decode("utf-8", errors='ignore'), 
                  get_bin_source_code('https://secretariavirtual.ubu.es/', {}, {}).decode("utf-8", errors='ignore')]

        outputs = ['UBUVirtual - Aula Virtual de la Universidad de Burgos', 'Identificacin']

        for input_test, output_test in zip(inputs, outputs):
            result = get_title(input_test)
            self.assertTrue(result == output_test)

    def test_get_number_errors(self):
        self.assertTrue(get_number_errors(['https://github.com/phf1001/semisupervised-recommendation-atk-detection'], {}, {}) == 1)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)