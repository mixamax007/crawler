import json
import os, sys
import logging.config
from lxml import etree
from lxml.html.clean import Cleaner, clean_html

from lxml.html.soupparser import fromstring
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from helper.config import Config


class Parse:

    def __init__(self, buffer, config_path=None):
        self.buffer = buffer
        self.config = Config.setup_main_config(os.path.join(config_path, 'yandex.yml'))
        self.result = []
        self._cleaner = None
        self._logger = logging.getLogger(__name__)

    def make(self):
        tree = fromstring(self.buffer, features="html.parser")
        matches = tree.xpath(self.config.ul)
        ul = matches[0]
        lis = ul.xpath(self.config.li)
        data = {'pages': json.loads(tree.xpath(self.config.pages)[0]), 'data': []}

        for li in lis:
            cleaner = self.cleaner_li()
            tmp = {'snippet': etree.tostring(cleaner.clean_html(li), method="xml", encoding="UTF-8").decode()}

            tree_temp = fromstring(tmp['snippet'], features="html.parser")
            href = tree_temp.xpath(self.config.href)
            tmp['text'] = "\n".join(etree.XPath("//text()")(tree_temp))
            tmp['href'] = href[0]

            title = tree_temp.xpath(self.config.title)
            tmp['title'] = title[0]

            data['data'].append(tmp)

        self.result = data

    def cleaner_li(self):

        cleaner = Cleaner()
        cleaner.javascript = True
        cleaner.style = True
        cleaner.meta = True
        cleaner.safe_attrs_only = True
        cleaner.remove_tags = ['i', 'span', 'b', 'li']
        cleaner.safe_attrs = ['href']

        return cleaner
