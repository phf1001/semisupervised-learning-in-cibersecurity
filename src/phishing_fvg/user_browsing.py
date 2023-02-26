from phishing_utils import get_proxy

class user_browsing:

    def __init__(self, proxy=None):

        self.user = None
        self.password = None
        self.cookies = None

        if proxy is None:
            self.proxies = get_proxy()
        else:
            self.proxies = proxy

        self.user_agent = self.get_user_agent()
        self.header = self.get_simple_user_header_agent()

    def set_standard_header(self, url):

        self.header = { "Host": url,
                        "User-Agent": self.user_agent,
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                        "Sec-Fetch-User": "?1"}

    @staticmethod
    def get_user_agent():
        return 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0'

    @staticmethod
    def get_simple_user_header_agent():
        return {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0'}

