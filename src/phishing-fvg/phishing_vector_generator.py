import numpy as np
import re
from user_browsing import user_browsing
from urllib.parse import urlparse
from os import path
from bs4 import BeautifulSoup
from phishing_utils import *


class PHISH_FVG:

    def __init__(self, url):

        self.url = url
        parsed = urlparse(url)
        self.base = parsed.netloc
        self.path = self.base + '/'.join(path.split('/')[:-1])

        self.fv = np.array([-1 for i in range(19)])

        self.user = user_browsing()
        self.user.set_standard_header(self.base)

        response_content = get_bin_source_code(self.url, self.user.get_simple_user_header_agent(), self.user.proxies) 
        self.html = response_content.decode("utf-8", errors='ignore')
        self.soup = BeautifulSoup(response_content)

        self.hyperlinks = find_hyperlinks(self.html)


    def set_feature_vector(self):

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

        if self.url.count('.') >= 4:
            self.fv[0] = 1

        else:
            self.fv[0] = 0


    def set_f2(self):
        """
        Sets F2.
        F2 = 1, if URL contains '@' or '-' symbols
        F2 = 0, otherwise
        """

        if '@' in self.url or '-' in self.url:
            self.fv[1] = 1

        else:
            self.fv[1] = 0


    def set_f3(self):
        """
        Sets F3.
        F3 = 1, if URL length >= 74
        F3 = 0, otherwise
        """

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

        splitted_url = get_splitted_url(self.url)
        suspicious_words = get_suspicious_keywords()

        for word in splitted_url:
            leet_translation = translate_leet_to_letters(word) #Decisión propia
            
            if bool(suspicious_words & leet_translation):
                self.fv[3] = 1
                return

        self.fv[3] = 0


    def set_f5(self):
        """
        Sets F5.
        F5 = 1, if tlds in URL > 1
        F5 = 0, otherwise

        # REVISAR COMPUESTOS
        """

        splitted_url = set(get_splitted_url(self.url))
        tlds = get_tlds_set()

        if len(splitted_url & tlds) > 1:
            self.fv[4] = 1

        else:
            self.fv[4] = 0


    def set_f6(self):
        """
        Sets F6.
        F6 = 1, if http count in URL > 1
        F6 = 0, otherwise
        """

        if len(re.findall('http', self.url)) > 1:
            self.fv[5] = 1

        else:
            self.fv[5] = 0


    def set_f7(self):
        """
        Sets F7.
        F7 = 1, if brand in incorrect position.
        F7 = 0, otherwise
        # Unitarias
        """

        targets = get_phishing_targets_set()
        parsed = urlparse(self.url.lower())
        base = remove_tld(parsed.netloc)
        base = remove_tld(base)
        path = parsed.path

        for target in targets:
            if target in base or target in path:
                self.fv[6] = 1
                return

        self.fv[6] = 0


    def set_f8(self):
        """
        Sets F8.
        F8 = 1, if data URI present in website.
        F8 = 0, otherwise

        Syntax: data:[<mime type>][;charset=<charset>][;base64],<encoded data>
        """

        matches = re.findall('data:(?:[^;,]*)?(?:;charset=[^;,]*)?(?:;base64)?,[^)"\';>]*[^)"\';>]', self.html)
        
        if len(matches) > 0:
            self.fv[7] = 1

        else:
            self.fv[7] = 0
            

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

            for i in range(len(forms_found)):
                form_found = forms_found[i]
                action_content = re.findall('(?:action=\")([^"]*)(?:\")', form_found)

                if len(action_content) > 0:

                    if is_empty(action_content[0]):
                        self.fv[8] = 1
                        return

                    elif is_simple_php_file(action_content[0]):
                        self.fv[8] = 1
                        return

                    elif is_foreign(self.url, action_content[0]):
                        self.fv[8] = 1
                        return
                        
        self.fv[8] = 0


    def set_f10_f11(self):
        """
        Sets F10 and F11.

        F10 = number of hyperlinks in source code.

        F11 = 1, if no hyperlinks found in source.
        F11 = 0, otherwise
        """

        n_hyperlinks_found = len(self.hyperlinks)
        self.fv[9] = n_hyperlinks_found

        if n_hyperlinks_found == 0:
            self.fv[10] = 1

        else:
            self.fv[10] = 0


    def set_f12(self):
        """
        Sets F12.

        ratio = |n_foreign_hyp| / |n_hyp|

        F12 = 1 if ratio > 0.5 and n_hyp > 0
        F12 = 0 otherwise

        REVISAR
        """

        if len(self.hyperlinks) < 1:
            self.fv[11] = 1 # Debería ser 0 pero es mejor 1 ya que es phishing clarísimamente
            return
            
        n_foreigns = get_number_foreign_hyperlinks(self.url, self.hyperlinks)
        ratio = (n_foreigns / len(self.hyperlinks))

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

        REVISAR
        """

        if len(self.hyperlinks) < 1:
            self.fv[12] = 1 # Debería ser 0 pero es mejor 1 ya que es phishing clarísimamente
            return
            
        n_empty = get_number_empty_hyperlinks(self.hyperlinks)
        ratio = (n_empty / len(self.hyperlinks))

        if ratio > 0.34:
            self.fv[12] = 1
        else:
            self.fv[12] = 0


    def set_f14(self):
        """
        Sets F14.

        ratio = |n_errors_hyp| / |n_hyp|

        F13 = 1 if ratio > 0.3 and n_hyp > 0
        F13 = 0 otherwise

        REVISAR
        """

        if len(self.hyperlinks) < 1:
            self.fv[13] = 1
            return
            
        n_errors = get_number_errors(self.hyperlinks, self.user.header,  self.user.proxies)
        ratio = (n_errors / len(self.hyperlinks))
        print(ratio)

        if ratio > 0.3:
            self.fv[13] = 1
        else:
            self.fv[13] = 0

    
    def set_f15(self):
        """
        Sets F15.

        ratio = |n_redirects| / |n_hyp|

        F13 = 1 if ratio > 0.3 and n_hyp > 0
        F13 = 0 otherwise

        REVISAR
        """

        if len(self.hyperlinks) < 1:
            self.fv[14] = 1
            return
            
        n_redirects = get_number_redirects(self.hyperlinks, self.user.header,  self.user.proxies)
        ratio = (n_redirects / len(self.hyperlinks))
        print(ratio)

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
                self.fv[15] = 1
                return

        self.fv[15] = 0 


    def set_f17(self):
        """
        Sets F17.
        F17 = 0 if copyright keyword matches base domain
        F17 = 1, otherwise
        """

        copyright_clues = ['©', '& copy', '&copy', 'copy', 'copyright', 'copyright', 'all right reserved', 'rights', 'right'] #'@', 

        for clue in copyright_clues:

            regex = '(?:{})([^<.>"]*)(?:[<.>"])'.format(clue)
            copy_contents = re.findall(regex, self.html)

            for copy_content in copy_contents:
                copy_content = remove_punctuation(copy_content).reshape(1)

                for content in copy_content[0].split():
                    if re.findall(content.replace(",", ""), self.base, re.IGNORECASE):
                        self.fv[16] = 0
                        return
        
        self.fv[16] = 1

    def set_f18(self):
        """
        Set F18.
        F18 = 1 if no keyword matches domain name
        F18 = 0 Otherwise
        """
        
        keywords = get_site_keywords(self.html)

        for keyword in keywords:

            if re.findall(keyword, self.base):
                self.fv[17] = 0
                return
        
        self.fv[17] = 1


    def set_f19(self):
        """
        Sets F19.
        F19 = 1, if foreign domain found in favicon link
        F19 = 0, otherwise
        """

        icons = self.soup.findAll("link", rel="icon") + self.soup.findAll("link", rel="shortcut icon")

        for icon in icons:

            link = extract_url_href(icon)

            if is_foreign(self.url, link):
                self.fv[18] = 1
                return

        self.fv[18] = 0 