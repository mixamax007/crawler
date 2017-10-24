
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from random import randint
import os, sys
import logging.config
from datetime import date
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from proxy.pproxy import ProxyManager

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(CURRENT_DIR, '..', 'config')

from pyvirtualdisplay import Display


class ConnectManager:
    def __init__(self, path_user_agents, service_log):
        self.count = 0
        self.freeDrivers = []
        self.drivers = []
        self.headers = []
        self.service_log = service_log
        fileAgents = open(path_user_agents)
        self._logger = logging.getLogger('crawler')
        for agent in fileAgents:
            self.headers.append(agent)
        self.display = Display(visible=0, size=(1920, 1080)).start()

    def erase(self, driver):
        self.freeDrivers.append(self.drivers.index(driver))

    def erase_all(self):
        self.freeDrivers = range(self.count)

    def create(self):
        manager = ProxyManager()
        prx = manager.get_proxy()

        if prx is None:
            self._logger.error("Can't create proxy")
            return None

        prx = prx.split('@')
        service_args = [
            '--proxy={}'.format(prx[-1]),
            '--proxy-type=https',
        ]
        if len(prx) == 2:
            service_args.append('--proxy-auth={}'.format(prx[0]))


        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = self.headers[randint(0, len(self.headers) - 1)]
        #
        dcap['phantomjs.page.customHeaders.Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        #dcap['phantomjs.page.customHeaders.Accept-Encoding'] = 'gzip, deflate, br'
        dcap['phantomjs.page.customHeaders.Accept-Charset'] = 'utf-8'
        dcap['phantomjs.page.customHeaders.Accept-Language'] = 'ru,en;q=0.8'
        dcap['phantomjs.page.customHeaders.X-Requested-With'] = 'XMLHttpRequest'
        dcap['phantomjs.page.customHeaders.Connection'] = 'Keep-Alive'
        dcap['phantomjs.page.customHeaders.Host'] = 'yandex.ru'

        service_log_path = os.path.join(self.service_log, 'ghostdriver.log.' + str(date.today()))

        driver = webdriver.PhantomJS(service_args=service_args, desired_capabilities=dcap, service_log_path=service_log_path)
        # driver = webdriver.PhantomJS(desired_capabilities=dcap,
        #                              service_log_path=service_log_path) #without proxy
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)

        return driver

    def get_driver(self):

        if not self.freeDrivers:

            proxy_created = self.create()

            if not proxy_created:
                return None

            self.drivers.append(proxy_created)
            self.count += 1

            return self.drivers[-1]

        idx = self.freeDrivers.pop()
        return self.drivers[idx]

    def restart(self, driver):
        num = self.drivers.index(driver)

        self.drivers[num].close()

        proxy_created = self.create()

        if not proxy_created:
            return False

        self.drivers[num] = proxy_created

        return self.drivers[num]
