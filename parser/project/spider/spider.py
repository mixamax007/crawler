import logging.config
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from spider.connect import ConnectManager

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(CURRENT_DIR, '..', 'config')


class Spider(object):
    def __init__(self, placeFrom, main_config):

        self.placeFrom = placeFrom
        self.manager = ConnectManager(path_user_agents=os.path.join(config_path, "userAgents.txt"),
                                      service_log=main_config['service_agent_conf_path'])
        self._logger = logging.getLogger('crawler')

    def load(self, url):
        data = {'url': None, 'document': None}

        try:

            driver = self.manager.get_driver()
            if not driver:
                return None

        except Exception as err:
            self._logger.error(err)
            raise err

        driver.get(self.placeFrom + url)
        data['url'] = url
        data['document'] = driver.page_source
        self.manager.erase(driver)
        return data
