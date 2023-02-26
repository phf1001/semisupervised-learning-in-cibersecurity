import json
import os
import time
from proxy_tor import proxy_tor
from multiprocessing import Process

if __name__ == '__main__':
    """
    Entry point for the script. 
    Check pysocks dependencies.
    """

    try:
        n_desired_proxies = int(input('\nNumber of desired proxies: '))
        counter = 0
        available_proxies = []

        while len(available_proxies) < n_desired_proxies:
            left = n_desired_proxies - len(available_proxies)

            proxies = [proxy_tor(i) for i in range(counter, counter + left)]
            workers = [
                Process(target=proxy.launch_file, args=()) for proxy in proxies
            ]

            for w in workers:
                w.start()

            new_available_ips = [proxy.get_ip() for proxy in proxies]
            new_available_proxies = [{
                'http':
                f'socks5h://127.0.0.1:{proxy.socks_port}'
            } for proxy in proxies]
            new_available_proxies = [
                proxy
                for ip, proxy in zip(new_available_ips, new_available_proxies)
                if ip != ''
            ]

            counter += left
            available_proxies += new_available_proxies
            time.sleep(3)

        print(f'\n\n-> Available proxies: {available_proxies}')

        with open('../phishing_fvg/data/proxies.json', 'w') as f:
            json.dump(available_proxies, f)
            f.close()

        while True:
            pass

    except KeyboardInterrupt:

        if len(workers) > 0:
            for w in workers:
                w.terminate()

        for id_file in range(counter):

            tor_file = f'/etc/tor/torrc.{id_file}'
            if os.path.exists(tor_file):
                os.remove(tor_file)
