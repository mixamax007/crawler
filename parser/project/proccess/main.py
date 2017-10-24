import os
import sys
import pika
import json
import redis
from collections import namedtuple
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from mongoengine import connect
from helper.config import Config
from proccess.proccessing import Process
import logging.config
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(CURRENT_DIR, '..', 'config')

main_config = Config.setup_main_config(os.path.join(config_path, 'main.yml'))
logging.config.fileConfig(os.path.join(config_path, 'logging.conf'))
params = Config.setup_main_config(os.path.join(config_path, 'rabbit.yml'))


class RabbitTask:

    def __init__(self):

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(params.receiver.host))
        self._logger = logging.getLogger(__name__)
        self.queue = params.receiver.queue.social

        self._channel = self.connection.channel()
        self._channel.queue_declare(queue=self.queue, durable=True)
        self._channel.basic_qos(prefetch_count=1)

    def callback(self, ch, method, properties, body):

        self._logger.debug(body)
        task = json.loads(body.decode(), object_hook=lambda d: namedtuple('task', d.keys())(*d.values()))

        self._logger.debug(" [x] Received {} from {}".format(task, method.routing_key))

        if type(task.redisPassword) is None:

            rd = redis.Redis(
                host=task.redisHost,
                port=task.redisPort)
        else:
            rd = redis.Redis(
                host=task.redisHost,
                port=task.redisPort,
                password=task.redisPassword
            )
        rd.set(task.ID, 2)
        re = rd.get(task.ID)
        self._logger.debug(re)

        ch.basic_ack(delivery_tag=method.delivery_tag)

        self._logger.debug(task)
        config = {'service_agent_conf_path': main_config.service_agent_conf_path,
                  'task_id': task.ID,
                  'mongo': {'host_addr': task.mongoServerName,
                            'db_name': task.mongoDataBaseName,
                           }
                 }

        for query in task.settings.search_q:
            payload = {'text': query}
            process = Process(main_config=config, searcher=task.settings.searcher, params={'ID': task.ID})
            self._logger.debug('start processing')
            process.create_query(payload, pages=task.settings.count)
            rd.set(task.ID, 3)
            self._logger.debug('end processing')


class SomeTaskManager(RabbitTask):

    def main(self):

        self._channel.basic_consume(self.callback, queue=self.queue, no_ack=False)

        self._logger.debug(' [*] Waiting for messages. To exit press CTRL+C')
        self._channel.start_consuming()


if __name__ == '__main__':
    sm = SomeTaskManager()
    sm.main()
