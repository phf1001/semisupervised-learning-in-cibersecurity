import os
import shlex
import re
import requests


class proxy_tor:

    def __init__(self, number_instance):

        self.number_instance = number_instance
        self.socks_port = (9052 + 2 * number_instance)  # Default tor 9050
        self.control_port = (9053 + 2 * number_instance)  # Default tor 9051
        self.hash = '16:52F8D50726E4C0D2605124196C6B846377A62ABB9F998C51E0C77CF20C'
        self.file = self.create_tor_file()

    def get_ip(self):

        state = os.system(f'curl --proxy socks5h://localhost:{self.socks_port} http://ipinfo.io/ip ')

        if state == 0:
            given_ip = requests.get(
                'http://ipinfo.io/ip', proxies={'http': f'socks5h://127.0.0.1:{self.socks_port}'}).text

            if len(re.findall(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", given_ip)) > 0:
                return given_ip

        return ''

    def create_tor_file(self):

        file_path = f'/etc/tor/torrc.{self.number_instance}'

        with open(file_path, 'w') as f:
            f.write(f'''
                    SocksPort {self.socks_port}
                    ControlPort {self.control_port}
                    DataDirectory /var/lib/tor{self.number_instance}
                    HashedControlPassword {self.hash}
                    ''')
            f.close()

        return file_path

    def launch_file(self):
        os.system(f'tor -f {self.file} > /dev/null')
