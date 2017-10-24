import pika
import os,sys
import logging.config
from social.config import Config
import json

class Sender:

    def __init__(self, params):
        self.params = params
        self._connection = None
        self._channel = None

    @property
    def connection(self):
        if not self._connection:
            self._connection = pika.BlockingConnection(pika.ConnectionParameters(self.params.sender.host))

        return self._connection

    @connection.setter
    def connection(self, value):
        self._connection = value

    @property
    def channel(self):
        if not self._channel:
            self._channel = self.connection.channel()
        return self._channel

    @channel.setter
    def channel(self, value):
        self._channel = value

    def send(self, severity, text):
        self.channel.queue_declare(queue=severity, durable=True)
        self.channel.basic_publish(exchange='',
                              body=json.dumps(text),
                              routing_key=severity,
                              properties=pika.BasicProperties(
                                  delivery_mode=2, )
                              )

    def send_and_close_connection(self, text, severity):
        self.send(severity, text)
        self.close_all()

    def close_channel(self):
        self.channel.close()
        self.channel = None

    def close_connection(self):
        self.connection.close()
        self.connection = None

    def close_all(self):
        self.close_channel()
        self.close_connection()


class SenderSocial(Sender):
    def __init__(self, params):
        super().__init__(params)

    def send_and_close_connection(self, text, severity=None):

        severity = self.params.sender.queue.social
        super().send_and_close_connection(text, severity)

    def send_and_close_channel(self, text):

        severity = self.params.sender.queue.social
        self.send(severity, text)
        self.close_channel()



if __name__ == '__main__':
    #pass
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(CURRENT_DIR,'..', 'config')
    logging.config.fileConfig(os.path.join(config_path, 'logging.conf'))
    logger = logging.getLogger(__name__)
    params = Config.setup_main_config(os.path.join(config_path, 'rabbitmq.yml'))
    # logger.debug(params.sender.exchange)
    # logger.debug(type(params.sender.exchange))
    sc = SenderSocial(params)
    sc.send_and_close_connection(text='Baaaah-0')
    sc.send_and_close_connection(text='Baaaah-1')
    sc.send_and_close_connection(text='Baaaah-2')