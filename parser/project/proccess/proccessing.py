import datetime
import logging.config
import os
import sys
from urllib.parse import urlencode, quote_plus
import logging.config
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from mongoengine import connect
from parse.parsing import Parse
from spider.spider import Spider
from structure.Page import Page

import hashlib

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(CURRENT_DIR, '..', 'config')
logging.config.fileConfig(os.path.join(config_path, 'logging.conf'))

class Process:
    def __init__(self, main_config, searcher, params):
        self.main_config = main_config
        self.searcher = searcher
        self._sp = None
        self.main_result = []
        self.params = params
        self._logger = logging.getLogger(__name__)

    @property
    def sp(self):
        if not self._sp:
            self._sp = Spider(placeFrom=self.searcher, main_config=self.main_config)
        return self._sp

    def create_query(self, payload, pages=3):

        if pages > 0:
            while True:
                if self.main_result:
                    try:
                        page_next = self.main_result[-1]['pages']['pager']['nextPage']
                        if not (type(page_next) == bool and page_next is False) and page_next < pages:
                            payload.update({'p': page_next})
                            self.get_query(payload)
                        else:
                            break
                    except Exception as err:
                        self._logger.debug(err)
                        break

                else:
                    try:
                        self.get_query(payload)
                    except Exception as err:
                        self._logger.debug(payload)
                        self._logger.debug(err)
                        break

        try:
            self.create_records(payload)
        except Exception as err:
            self._logger.debug(err)

    def create_records(self, payload):
        self._logger.debug(self.params)

        connection_url = "{}/{}".format(self.main_config['mongo']['host_addr'].rstrip("/"),
                                        self.main_config['mongo']['db_name'])
        self._logger.debug(connection_url)
        connect(host=connection_url)

        for record in self.main_result:
            for index, d in enumerate(record['data'], 1):
                uniq_id = hashlib.md5((d['href'] + '_' + d['snippet']).encode('utf-8')).hexdigest()
                if not Page.objects(uniq_id=uniq_id).count():
                    item = Page()
                    item.title = d['title']
                    item.text = d['text']
                    item.url = d['href']
                    item.snippet_number = index * (payload.get('p', 0) + 1)
                    item.search_query = payload['text']
                    item.uniq_id = str(uniq_id)
                    item.task_id = [self.params['ID']]
                    item.save()
                    self._logger.debug("record saved with uniq_id {}".format(uniq_id))
                else:
                    Page.objects(ID=uniq_id).update_one(add_to_set__task_id=self.params['ID'])
                    self._logger.debug("record update with uniq_id {}".format(uniq_id))

    def get_query(self, payload):

        #url_format = urlencode(payload, quote_via=quote_plus)
        self._logger.debug(payload)
        url_format = urlencode(payload)
        url = "search/?{}".format(url_format)

        pages_result = {}

        try:
            #test

            # buffer = open(os.path.join(CURRENT_DIR,"../", "test", "files", "result3.html"), "r", encoding='UTF-8')
            # pages_result = {'document': buffer}

            #production

            if self.sp:
                self._logger.debug("sp")
                pages_result = self.sp.load(url)
        except Exception as err:
            self._logger.error("Can't load page {} ".format(url))
            raise err
        else:
            if pages_result:
                parse = Parse(pages_result['document'], config_path=config_path)
                parse.make()
                pages_result.update(parse.result)
                self.main_result.append(pages_result)
