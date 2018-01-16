docker run -d --name redis01 redis
docker run --name mysql01 -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -d mysql
sleep 15 
docker exec -ti mysql01 sh -c 'exec mysql -e "create database jumpserver default charset 'utf8';" -uroot -p"root" '  
docker logs mysql01
#docker run -ti --rm --link=mysql01:mysql01 --link redis01:redis01 henryzhang1/jumpserver /usr/bin/python3 /opt/jumpserver/apps/manage.py makemigrations
#docker run -ti --rm --link=mysql01:mysql01 --link redis01:redis01 henryzhang1/jumpserver /usr/bin/python3  /opt/jumpserver/apps/manage.py migrate
docker run -ti --rm --link=mysql01:mysql01 --link redis01:redis01 henryzhang1/jumpserver bash -c 'cd /opt/jumpserver/utils && /usr/bin/python3  /opt/jumpserver/apps/manage.py makemigrations && python3 /opt/jumpserver/apps/manage.py migrate'
docker run --name jms01 --link=mysql01:mysql01 --link redis01:redis01 -p 2222:2222 -p 80:80 henryzhang1/jumpserver
