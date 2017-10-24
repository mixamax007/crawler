#!/usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess
from time import sleep
import subprocess
import requests, os
import json

def run(app, *args):
    check_call([app] + list(args))


if __name__ =="__main__":

    command = "ip addr | grep -E 'eth0.*state UP' -A2 | tail -n 1 | awk '{print $2}' | cut -f1 -d '/'"  # the shell command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)

    output = process.communicate()
    IP = output[0].decode("utf-8").strip("\n")
    NAME = "flask-service"
    HOST = os.getenv('CONSUL_HOST')
    PORT = 5000

    message = dict()
    message["Name"] = NAME
    message["address"] = IP
    message["port"] = PORT

    temp = dict()
    temp["http"] = "http://{}:{}".format(IP, PORT)
    temp["interval"] = "5s"

    message["Check"] = temp.copy()

    temp = dict()
    temp["somekey"] = "somevalue"

    message["NodeMeta"] = temp
    url = 'http://{}:8500/v1/agent/service/register'.format(HOST)
    print(url)
    print(message)
    r = requests.put(url, data=json.dumps(message))
    print(r.text)
