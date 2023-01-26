import json
from proxy_tor import proxy_tor
from multiprocessing import Process

# Check pysocks dependencies

if __name__ == '__main__':

    try:
        n_proxies = 2
        proxies = [proxy_tor(i) for i in range(n_proxies)]
        workers = [Process(target=proxy.launch_file, args=()) for proxy in proxies]

        for w in workers:
            w.start()
        
        available_ips = [proxy.get_ip() for proxy in proxies]
        available_proxies = [{'http' : 'socks5h://127.0.0.1:{}'.format(proxy.socks_port)} for proxy in proxies]
        available_proxies = [proxy for ip, proxy in zip(available_ips, available_proxies) if ip != '']
        print('Available proxies: {}' .format(available_proxies))

        with open('proxies.json', 'w') as f:
            json.dump(available_proxies, f)
            f.close()

        while True:
            pass


    except KeyboardInterrupt:
        
        for w in workers:
            w.terminate()
        exit()