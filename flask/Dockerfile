FROM ubuntu:16.04
 RUN apt-get update -y && apt-get install -y python3 python3-dev python3-pip nano curl
 RUN mkdir /usr/src/log
 ADD requirements.txt /
 RUN pip3 install -r requirements.txt
 RUN apt-get install -y uwsgi-plugin-python3
 RUN mkdir /var/log/uwsgi
 RUN pip3 install uwsgi
 ADD utils/entrypoint.py /
 WORKDIR /usr/src/app
 RUN chmod 777 /entrypoint.py
 CMD /entrypoint.py