FROM debian
RUN apt-get update && apt-get install -y  software-properties-common gnupg -y 
RUN apt-get install -y vim wget gcc automake redis-server git  libssl-dev zlib1g-dev make python3-pip libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk libffi-dev -y libkrb5-dev libmysql++-dev python-dev libldap2-dev libsasl2-dev libssl-dev nginx sshpass
RUN ln -s /usr/local/bin/pip3 /usr/local/bin/pip
RUN ln -s /usr/local/bin/python3 /usr/local/bin/python
RUN cd /opt/ &&git clone https://github.com/henry-zhang/coco.git && cd coco && git checkout dev && cd requirements && pip3 install -r requirements.txt
COPY ./jms-core/ /opt/jumpserver/
#RUN  cd /opt/ && git clone https://github.com/henry-zhang/jumpserver.git && cd jumpserver && git checkout dev
RUN cd /opt/jumpserver/requirements && pip3 install -r requirements.txt
RUN rm /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python &&ln -s  /usr/bin/pip3 /usr/bin/pip
COPY luna /opt/luna
COPY nginx/default /etc/nginx/sites-enabled/
#COPY coco/conf.py /opt/coco/
RUN apt-get clean
CMD  nginx &&cd /opt/jumpserver&& /usr/bin/python3 run_server.py all
#& cd /opt/coco/ && /usr/bin/python3 run_server.py 



