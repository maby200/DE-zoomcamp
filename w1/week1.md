# Week 1

Reminders: the containers that has the data are: pgadmin and pg-database

Data will be taken from:
`https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz `
## Run posgres container
```bash
sudo docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    postgres:13
```

```bash
head -n 100
```

## An error faced trying to run postgres

The error I got was:

```bash
(.env) usr@usr:~/path/w1$ pgcli -h localhost -p 5432 -u root -d ny_taxi
Password for root: 
connection failed: password authentication failed for user "root"
```
A huge thanks to Gonzalo Alcalá and Annet who helped me go though this problem.

---
(I used Ubuntu 20.04 for this)

I put `sudo` before any docker command. Idk  why yet.


First I had to verify:
```bash
sudo docker ps
```
And verify nothing is running on port 5432

E.g.:
```
$ sudo docker ps
CONTAINER ID    IMAGE             ...  PORTS                                        ...
16611269jk34l   postgres:latest   ...  0.0.0.0:5432->5432/tcp, :::5432->5432/tcp    ...
```


If something is running on that port
```bash
$ sudo docker stop *containerID*
```
(it is not necessary to write all the ID's digit you only need the first 4 digits )

E.g.:
```bash
$ sudo docker stop 1661
```

Then see whats running on that port. To see that:
```bash
$ sudo lsof -i :<port N°>
```
In my case I am looking what is running on port 5432:

```bash
$ sudo lsof -i :5432

## and found this

COMMAND    PID USER    FD   TYPE  DEVICE   SIZE/OFF NODE  NAME
docker-pr 1234 root    4u   IPv4  43978      0t0     TCP  *:postgresql (LISTEN)
docker-pr 4321 root    4u   IPv6  52077      0t0     TCP  *:postgresql (LISTEN)
```
So that means I have to kill those processess.

```bash
$ kill -9  <PID N° >
```
E.g: In my case the PIDs are 2366 and 2387
```bash
$ kill -9  1234
$ kill -9  4321
```
Now it's time to delete the `ny_taxi_postgres_data`
```bash
$ sudo rm -rf ny_taxi_postgres_data
```
Now it's time to follow again the process of running postgres. As Annet recommends:
```bash
docker run -it \
....  
-p 5433:5432\ 
postgres:13
```
Where 5433 will be the number to use in ypur connection using `pgcli`:
```bash
pgcli -h localhost -p 5433 -u root -d ny_taxi
```

Hope that helps!

--- 

## Comandos
```bash
$ head -n 100 nombre_archivo.csv > archivo_donde_se_guardara.csv
```

## Running Jupyter with virtualenvironment (in case you dont have Anaconda)
First ensure you have your virtualenv activated:
In linux:
```bash
$ source (name_of_your_env)/bin/activate
```
To add kernel to your jupyter environment:
```bash
$ ipython kernel install --user --name=venv
```

After finishing your work it's advisable to delete that kernel, so:
```bash
$ jupyter-kernelspec uninstall venv
```

Useful commands
```
$ jupyter-kernelspec --help
$ jupyter-kernelspec list
```

## Connecting to pgAdmin
You can remove the network later with the command docker network rm pg-network .

You can look at the existing networks with docker network ls .

An advice from @ziritrion is that we have to create a docker network so:
`docker network create pg-network`

Now re running postgres but in that network:
```bash
sudo docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    --network=pg-network \
    --name pg-database \
    postgres:13
```

```bash
sudo docker run -it \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    -p 8080:80 \
    --network=pg-network \
    --name pgadmin \
    dpage/pgadmin4
```

## Los datos no se sobrescriben ni nada porque primero  se detuvo el docker. Antes de crear docker network

# Using ingestion script wiht Docker

Para convertir jupyter to .py file
jupyter nbconvert --to=script upload-data.ipynb

## To run your pipeline just type the following:
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz "

python ingest_data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --db=ny_taxi \
    --table_name=yellow_taxi_trips \
    --url=${URL}

# Dockerizing the script
Change Dockerfile in your dir

Build: (that "." is for building here? )

`$ sudo docker build -t taxi_ingest:v001 . `

And then:
sudo docker run -it \
    --network=pg-network \
    taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pg-database \
    --port=5432 \
    --db=ny_taxi \
    --table_name=yellow_taxi_trips \
    --url=${URL}

# Running Postgres and pgAdmin with Docker-compose

In the videoclass there was some "issue" (not that much) that Alexey said it wasn't possible to make a persistent connection for pgadmin. And @ziritrion added a way to do so:

But before, make sure to creare a folder `data_pgadmin`.

Note: to make pgAdmin configuration persistent, create a folder data_pgadmin. Change its permission via

```bash
sudo chown 5050:5050 data_pgadmin
```

Then we're ready to write ziritrion's file:

`docker-compose.yaml`:
```yml
services:
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=ny_taxi
    volumes:
      - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    ports:
      - "5432:5432"
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    volumes:
      - "./data_pgadmin:/var/lib/pgadmin"
    ports:
      - "8080:80"
```
Before running it we have to make sure nothing is running on the ports specified 5432, 8080 or 80 (not sure about the last one).
For that:
```bash
$ sudo docker ps
CONTAINER ID  IMAGE           COMMAND                ... PORTS                                           NAMES
a21ae8ryh154  dpage/pgadmin4  "/entrypoint.sh"       ... 443/tcp, 0.0.0.0:8080->80/tcp, :::8080->80/tcp  pgadmin
wercfa123712  postgres:13     "docker-entrypoint.s…" ... 0.0.0.0:5432->5432/tcp, :::5432->5432/tcp       pg-database
```
I have to stop those containers since are running on the ports I want to run my `docker-compose.yaml`

Run `sudo docker stop pgadmin` and `sudo docker stop pg-database` (you can use the first 4 digits of the containers instead of the NAMES)

To make sure all the ports are clear run again: `sudo docker ps` and there shouldn't be any of the previous containers.


En la tarea:

Dockerfile se necesita para poder hacer data ingestion con python (no se si en otras formas se pueda)

Escribe tu `ingest_data.py`

`sudo docker build -t greentaxi_ingest:homweork1 .  ` <-Nótese el punto de ahí, es importante!

Recuerda el nombre de tu ingest: greentaxi_ingest:homweork1

busca la network donde está tu docker compose (tranca porque no has especificado cuál.. :c)

Pero [dicen](https://docs.docker.com/compose/networking/) que cuando haces docker compose up, se crea la network myapp_default:

For example, suppose your app is in a directory called myapp, and your docker-compose.yml looks like this:
When you run docker compose up, the following happens:

    A network called myapp_default is created.
    A container is created using web’s configuration. It joins the network myapp_default under the name web.
    A container is created using db’s configuration. It joins the network myapp_default under the name db.

Entonces la encontré:
homework_default


ahora correré:

```bash
sudo docker run -it \
    --network=homework_default \
    greentaxi_ingest:homweork1 \
    --user=root \
    --password=root \
    --host=pgdatabase \
    --port=5432 \
    --db=ny_taxi \
    --table_name_1=green_trips \
    --table_name_2=taxi_zones
```