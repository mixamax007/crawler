#!/usr/bin/python3
from subprocess import check_call, call, Popen, PIPE
from time import sleep


def run(app, *args):
    check_call([app] + list(args))

if __name__ =="__main__":

    run('rm', '-f', '/etc/nginx/conf.d/default.conf')
    out = 0
    while int(out) == 0:
        pdump = Popen(["nmap", "127.0.0.1"], stdout=PIPE)
        parch = Popen(["grep", "5432"], stdin=pdump.stdout, stdout=PIPE)
        pln = Popen(["wc", "-l"], stdin=parch.stdout, stdout=PIPE)
        out, err = pln.communicate()
    run("nginx", "-g", "daemon off;")

    while True:
        sleep(10)