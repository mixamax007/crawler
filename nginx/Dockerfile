FROM nginx:latest
 RUN apt-get update && apt-get install -y nano
 COPY ./nginx.conf /etc/nginx/nginx.conf
 COPY ./flask.conf /etc/nginx/conf.d/flask.conf
 COPY ./utils/entrypoint.py /entrypoint.py
 CMD ["nginx", "-g", "daemon off;"]