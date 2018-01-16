docker run -d --name redis01 redis
docker run --name mysql01 -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=jumpserver -d mysql --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
sleep 30
docker logs mysql01
docker run -ti --rm henryzhang1/jumpserver /usr/bin/python3 /opt/jumpserver/apps/manage.py makemigrations
docker run -ti --rm henryzhang1/jumpserver /usr/bin/python3  /opt/jumpserver/apps/manage.py migrate
docker run --name jms01 --link=mysql01:mysql01 --link redis01:redis01 -p 2222:2222 -p 80:80 henryzhang1/jumpserver
