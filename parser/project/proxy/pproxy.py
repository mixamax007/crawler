import requests
import os, sys
import lxml.html as html
import time
import logging.config
import consul
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from helper.config import Config

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(CURRENT_DIR, '..', 'config')

main_config = Config.setup_main_config(os.path.join(config_path, 'main.yml'))
logging.config.fileConfig(os.path.join(config_path, 'logging.conf'))

class ProxyManager(object):

    def __init__(self):
        self.headers = {
            'User-Agent': 'Lynx/2.8.9dev.8 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/3.4.9',
            'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru,en-US;q=0.7,en;q=0.3',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'Keep-Alive',
            'Host': 'yandex.ru'
        }

        self.url = 'https://yandex.ru/search/?text=qwerty&lr=213'
        self._logger = logging.getLogger(__name__)
        self.download_url = 'http://api.foxtools.ru/v2/Proxy.txt' \
               '?cp=UTF-8&lang=Auto&type=HTTPS&available=Yes&free=Yes&uptime=5&limit='
        self._logger.debug("init")
        self.proxy_list_bad = []
        self.proxy_list_use = []
        self.proxy_list_clean = []
        self.CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
        self.scan_file = 'proxies.txt'

        consul_host = os.getenv('CONSUL_HOST', '127.0.0.1')
        consul_port = os.getenv('CONSUL_PORT', 8500)

        self.c = consul.Consul(host=consul_host, port=consul_port)

        index, self.proxy_list_clean = self.c.kv.get('crawler/proxy/accounts')

        if self.proxy_list_clean is None:
            self.proxy_list_clean = []
            self.proxy_list_clean = self.download_proxy()

        self._logger.debug("proxy list")
        proxy_list = list(self.proxy_list_clean)

        self._logger.debug(proxy_list)
        for proxy in proxy_list:
            self._logger.debug(proxy)
            
            if not self.check_proxy(proxy):
                self.proxy_list_clean.remove(proxy)


    def _read_proxies(self):

        return [line.rstrip('\n') for line in open(os.path.join(self.CURRENT_DIR, self.scan_file), 'r')]

    def get_proxy(self):
       
        self._logger.debug("start")
        proxy = None
        if self.proxy_list_clean:
            proxy = self.proxy_list_clean[0]

            self.proxy_list_clean.pop(0)
            self.proxy_list_use.append(proxy)
            
        self._logger.debug(proxy)
        return proxy

    def release_proxy(self, proxy):
        self.proxy_list_use.remove(proxy)
        self.proxy_list_clean.append(proxy)

    def download_proxy(self, amount=100):
        r = requests.get(self.download_url + str(amount), timeout=10)
        proxy_list = r.text.split('\r\n')[1:-1]
        proxy_list_full = self.proxy_list_clean + self.proxy_list_use + self.proxy_list_bad

        for proxy in proxy_list_full:
            if proxy in proxy_list:
                proxy_list.remove(proxy)

        return proxy_list

    def check_proxy(self, proxy):
        proxy_dict = {
            "https": "https://" + proxy,
        }

        try:
            r = requests.get(self.url, headers=self.headers, proxies=proxy_dict, timeout=10)
            if (r.status_code == 200) and (self._check_captcha(r.text)):
                return True
            else:
                return False
        except Exception as err:
            self._logger.debug(err)
            return False

    def _check_captcha(self, htmlr):
        page = html.fromstring(htmlr)
        if page.cssselect('.form__captcha') or htmlr[0] == '{':
            return False
        return True


if __name__ == '__main__':
    prx = ProxyManager()
    print(prx.get_proxy())
