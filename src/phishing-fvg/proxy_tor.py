import os
import re
import requests

class proxy_tor:

    def __init__(self, number_instance):

        self.number_instance = number_instance
        self.socks_port = (9050 + 2*  number_instance) #Default tor 9050
        self.control_port = (9051 + 2 * number_instance) #Default tor 9051
        self.hash = '16:52F8D50726E4C0D2605124196C6B846377A62ABB9F998C51E0C77CF20C' #tor --hash-password "contrasena"
        self.file = self.create_tor_file()


    def get_ip(self):

        state = os.system('curl --proxy socks5h://localhost:{} http://ipinfo.io/ip '.format(self.socks_port))

        if state == 0:
            given_ip = requests.get('http://ipinfo.io/ip', proxies={'http':'socks5h://127.0.0.1:{}'.format(self.socks_port)}).text
        
            if len(re.findall(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", given_ip)) > 0:
                return given_ip

        return ''


    def create_tor_file(self):

        file_path = '/etc/tor/torrc.{}'.format(self.number_instance)

        with open(file_path, 'w') as f:
            f.write('''
                    SocksPort {}
                    ControlPort {}
                    DataDirectory /var/lib/tor{}
                    HashedControlPassword {}
                    '''.format(self.socks_port, self.control_port, self.number_instance, self.hash))
            f.close()

        return file_path


    def launch_file(self):
        os.system('tor -f {} >/dev/null'.format(self.file))
