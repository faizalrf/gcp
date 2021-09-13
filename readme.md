# Mountkirk Game Implementation 6m11

This readme discusses how the deployment is done for the GKE cluster and the backend database.

Start by the following two to set the user and project in cloud shell.

```
$ gcloud auth list
$ gcloud config list project
```

Import the Kuberbetes magic to the cloud shell

```
$ source <(kubectl completion bash)
```

## GKE

### Create Game Cluster

Execute the `install.sh` from the root folder, the script calls the following 

```
./xonotic-game.sh
./config-xonotic-game.sh
./xonotic-gameservers.sh
./xonotic-ui.sh
./app/deploy.sh
```

- `xonotic-game.sh`

  This deploys the xonotic game GKE cluster in the `asia-southeast1` Singapore based on `e2-standard-2` with auto scaling, using the custom `demo-vpc`, and dedicated all three Singapore ZONES

  ```
  gcloud beta container --project group1-6m11 clusters create xonotic-game \
  --region asia-southeast1 \
  --cluster-version 1.20.8-gke.900 \
  --tags=game-server \
  --scopes=gke-default \
  --machine-type e2-standard-2 \
  --image-type "COS_CONTAINERD" \
  --disk-type "pd-standard" --disk-size 100 \
  --service-account "group1@group1-6m11.iam.gserviceaccount.com" \
  --num-nodes 1 \
  --logging=SYSTEM,WORKLOAD \
  --monitoring=SYSTEM \
  --enable-ip-alias --network "projects/group1-6m11/global/networks/demo-vpc" \
  --subnetwork "projects/group1-6m11/regions/asia-southeast1/subnetworks/subnet-sg" \
  --enable-autoscaling --min-nodes 1 --max-nodes 3 \
  --addons HorizontalPodAutoscaling,HttpLoadBalancing,NodeLocalDNS,GcePersistentDiskCsiDriver \
  --no-enable-autoupgrade \
  --enable-autorepair \
  --max-surge-upgrade 1 \
  --max-unavailable-upgrade 0 \
  --enable-shielded-nodes --shielded-secure-boot --shielded-integrity-monitoring \
  --node-locations "asia-southeast1-a","asia-southeast1-b","asia-southeast1-c"
  ```

- `config-xonotic-game.sh`
  
  This connects to the newly provisioned `xonotic-game` cluster
  
  ```
  export region_name=asia-southeast1
  export cluster_name=xonotic-game
  gcloud container clusters get-credentials $cluster_name --region $region_name
  ```

- `xonotic-gameservers.sh`
  
  This deploys the actual Xonotic Game on to the cluster, configure the namespace Realms, sets up the firewall for connectivity and finally gets the IP and port of the game server using `kubectl get gameserver`

  ```
  gcloud container clusters get-credentials xonotic-game --region=asia-southeast1

  kubectl create namespace agones-system

  kubectl apply -f https://raw.githubusercontent.com/googleforgames/agones/release-1.16.0/install/yaml/install.yaml

  sleep 1m

  kubectl get --namespace agones-system pods

  gcloud game servers realms create realm-xonotic \
  --time-zone Singapore \
  --location asia-southeast1

  gcloud game servers clusters create cluster-xonotic \
  --realm=realm-xonotic \
  --gke-cluster locations/asia-southeast1/clusters/xonotic-game \
  --namespace=default \
  --location asia-southeast1 \
  --no-dry-run

  gcloud game servers deployments create deployment-xonotic

  gcloud game servers configs create config-1 \
  --deployment deployment-xonotic \
  --fleet-configs-file xonotic_fleet_configs.yaml \
  --scaling-configs-file xonotic_scaling_configs.yaml

  gcloud game servers deployments update-rollout deployment-xonotic \
  --default-config config-1 --no-dry-run

  kubectl get fleet

  gcloud compute firewall-rules create gcgs-xonotic-firewall \
  --network demo-vpc \
  --allow udp:7000-8000 \
  --target-tags game-server \
  --description "Firewall to allow game server udp traffic"

  kubectl get gameserver
  ```

- `xonotic-ui.sh`

  This configures the Xonotic UI Pool within the `xonotic-game` cluster. With the same setup as the Xonotic Game pool with REGION as `asia-southeast1` and ZONES dedicated to all three for Singapore.

  ```
  gcloud container --project group1-6m11 node-pools create xonotic-ui-pool \
  --cluster xonotic-game \
  --region asia-southeast1 \
  --tags=game-ui \
  --machine-type e2-medium \
  --image-type "COS_CONTAINERD" \
  --disk-type "pd-standard" --disk-size 100 \
  --service-account "group1@group1-6m11.iam.gserviceaccount.com" \
  --num-nodes 1 \
  --enable-autoscaling --min-nodes 1 --max-nodes 3 \
  --no-enable-autoupgrade \
  --enable-autorepair \
  --max-surge-upgrade 1 \
  --max-unavailable-upgrade 0 \
  --shielded-secure-boot --shielded-integrity-monitoring \
  --node-locations "asia-southeast1-a","asia-southeast1-b","asia-southeast1-c" \
  --node-labels=pool=xonotic-ui-pool
  ```

- `deploy.sh`

  This script builds the local UI app container for SG clusters and pushes it to Google Container Registry `gcr.io` finally applys the YAML files to actually deploy this container on to the GKE cluster UI node pool, sets up load balancer with the help of ingress.

  ```
  docker build -t x-leaderboard:v${Version} .
  docker tag x-leaderboard:v${Version} gcr.io/$DEVSHELL_PROJECT_ID/x-leaderboard:v${Version}

  gcloud container clusters get-credentials xonotic-game --region asia-southeast1 --project group1-6m11
  docker push gcr.io/$DEVSHELL_PROJECT_ID/x-leaderboard:v${Version}

  kubectl apply -f deploy.yaml
  kubectl apply -f deploy-lb.yaml
  kubectl apply -f deploy-ingress.yaml
  
  kubectl autoscale deployment xonotic-ui --max 6 --min 1 --cpu-percent 60
  ```

  - `deploy.yaml`
    ```
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: xonotic-ui
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: xonotic-ui
      template:
        metadata:
          labels:
            app: xonotic-ui
        spec:
          containers:
          - name: x-leaderboard
            image: "gcr.io/group1-6m11/x-leaderboard:v1"
            ports:
            - containerPort: 8080
            env:
              - name: PORT
                value: "8080"
          nodeSelector:
            pool: xonotic-ui-pool 
    ```

  - deploy-lb.yaml
    
    To deploy the Load balancer that listens on port `80`, internally connecting to the app on `8080`

    ```
    apiVersion: v1
    kind: Service
    metadata:
      name: xonotic-ui
    spec:
      type: NodePort
      ports:
      - port: 80
        targetPort: 8080
      selector:
        app: xonotic-ui
    ```

  - `deploy-ingress.yaml`

    This links them all together by defining an ingress load balancer exposing the IP for the outside world

    ```
    apiVersion: networking.k8s.io/v1beta1
    kind: Ingress
    metadata:
      name: xonotic-ui
      annotations:
        kubernetes.io/ingress.class: gce
    spec:
      rules:
      - http:
          paths:
          - path: /*
            backend:
              serviceName: xonotic-ui
              servicePort: 80
    ```

Finally there is an `uninstall.sh` that can uninstall the entire setup with just one execution.

Once the above is done, we can execute the following to get the current app deployment status and the status of the cluster pods

```
$ kubectl get deployments
$ kubectl get svc,pods
```

Use the following to connect to the SG GKE cluster and to get the Load Balancer IP address / Port for the UI

```
$ gcloud container clusters get-credentials xonotic-game --region asia-southeast1 --project group1-6m11
$ kubectl get ingress

NAME         CLASS    HOSTS   ADDRESS          PORTS   AGE
xonotic-ui   <none>   *       34.102.207.237   80      22h
```

Use the following to connect to the SG GKE cluster and to get the IP and Port for the Xonotic Game

```
$ gcloud container clusters get-credentials xonotic-game --region asia-southeast1 --project group1-6m11
$ kubectl get gameserver

NAME         CLASS    HOSTS   ADDRESS          PORTS   AGE
xonotic-ui   <none>   *       34.102.207.237   80      22h
```

If we want to push new changes to the app, we can use the following two command, but ensure to update the build tag appropriately.

- `kubectl apply -f ./deploy.yaml`

To remove the deployment, by simply executing the following `delete` command. This will remove the app from the GKE UI pools.

- `kubectl delete -f ./deploy.yaml`

### Cloud Source Repo

Cloud source repository is used to setup and automate build and deployment for the UI component. To set up the repository locally using GCLOUD SDK either on the cloud shell or locally 

```
gcloud source repos create xonotic-app
gcloud source repos clone xonotic-app --project=group1-6m11
git config --global user.email "faisal.6m11@gmail.com"
git config --global user.name "Faisal 6m11"
git add *
git push -u origin master
```

## CloudSQL

CloudSQL using MySQL 8 is created using the google console and an game_user is created for connecting to the DB. 

Connect to the CloudSQL instance and execute the following commands to create a `game_user` within the database. 

```
MySQL [(none)]> create user game_user@'34.87.166.147' identified by 'password';
Query OK, 0 rows affected (0.005 sec)

MySQL [(none)]> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
| xonoticdb          |
+--------------------+
5 rows in set (0.002 sec)

MySQL [(none)]> grant all on xonoticdb.* to game_user@'34.87.166.147';
Query OK, 0 rows affected (0.006 sec)

MySQL [xonoticdb]> show tables;
+---------------------+
| Tables_in_xonoticdb |
+---------------------+
| game                |
| gameplayer          |
| leaderboard         |
| profile             |
+---------------------+
4 rows in set (0.002 sec)
```

Now the game_user can connect to the CLoudSQL instance from the static IP host, static IP is reqired and is configured under the networking part of the CloudSQL database.

- `player` table contains user profiles who have Xonotic game account
- `game` table is the current ongoing games master data and the past games that have ended
- `gameplayer` table contains the player list that have joined the game, current and past
- `leaderboard` contains the details of all the games such as
  - When did the player started playing that particular session
  - When did he die in game
  - Which player killed him

The leaderboard table can be used to query a particular game and identify who is the leader or identify the top 10 players in a game or, top 10 players across different game sessions.

***Note:** CloudSQL (MySQL 8.0) is needed for this, (MySQL 5.7 does not support Window Function SQL syntax)*

```
MySQL [xonoticdb]> desc player;
+-------------------+---------------------+------+-----+----------------------+--------------------------------------------------+
| Field             | Type                | Null | Key | Default              | Extra                                            |
+-------------------+---------------------+------+-----+----------------------+--------------------------------------------------+
| id                | bigint(20) unsigned | NO   | PRI | NULL                 | auto_increment                                   |
| name              | varchar(120)        | YES  |     | NULL                 |                                                  |
| email             | varchar(60)         | YES  |     | NULL                 |                                                  |
| inventory         | json                | YES  |     | NULL                 |                                                  |
| level             | smallint(6)         | YES  |     | NULL                 |                                                  |
| registration_date | timestamp(6)        | NO   |     | CURRENT_TIMESTAMP(6) | DEFAULT_GENERATED on update CURRENT_TIMESTAMP(6) |
+-------------------+---------------------+------+-----+----------------------+--------------------------------------------------+
6 rows in set (0.003 sec)

MySQL [xonoticdb]> desc game;
+---------------+---------------------+------+-----+----------------------+--------------------------------+
| Field         | Type                | Null | Key | Default              | Extra                          |
+---------------+---------------------+------+-----+----------------------+--------------------------------+
| id            | bigint(20) unsigned | NO   | PRI | NULL                 | auto_increment                 |
| game_name     | varchar(120)        | NO   |     | NULL                 |                                |
| total_players | int(11)             | NO   |     | NULL                 |                                |
| start_time    | timestamp(6)        | NO   |     | CURRENT_TIMESTAMP(6) | on update CURRENT_TIMESTAMP(6) |
| end_time      | timestamp(6)        | YES  |     | NULL                 |                                |
+---------------+---------------------+------+-----+----------------------+--------------------------------+
5 rows in set (0.002 sec)

MySQL [xonoticdb]> desc gameplayer;
+------------+---------------------+------+-----+---------+----------------+
| Field      | Type                | Null | Key | Default | Extra          |
+------------+---------------------+------+-----+---------+----------------+
| id         | bigint(20) unsigned | NO   | PRI | NULL    | auto_increment |
| game_id    | int(10) unsigned    | NO   |     | NULL    |                |
| player_id  | bigint(20)          | NO   | MUL | NULL    |                |
| start_time | timestamp(6)        | YES  |     | NULL    |                |
+------------+---------------------+------+-----+---------+----------------+
4 rows in set (0.002 sec)

MySQL [xonoticdb]> desc leaderboard;
+-------------+---------------------+------+-----+---------+----------------+
| Field       | Type                | Null | Key | Default | Extra          |
+-------------+---------------------+------+-----+---------+----------------+
| id          | bigint(20) unsigned | NO   | PRI | NULL    | auto_increment |
| game_id     | int(10) unsigned    | NO   |     | NULL    |                |
| player_id   | bigint(20)          | NO   |     | NULL    |                |
| killed_by   | bigint(20)          | YES  | MUL | NULL    |                |
| killed_time | timestamp(6)        | YES  |     | NULL    |                |
+-------------+---------------------+------+-----+---------+----------------+
5 rows in set (0.003 sec)
```

Connect to the `xonotic-sandbox` VM which is created with all the dependencies preset to connect to the CloudSQL database with the help of MySQL client and has all the necessary Python runtime components to be able to run the `xonotic-sim.py` game simulor.

The `xonotic-sim.py` was developed from scratch using Python 3.7, works up to 3.9. This is smart tool that is used to generat backend database, tables and populate test data. This is also used to create simulated game sessions and simulated live game matches which and eventually generate leaderboard data.

**`python3 xonotic-sim.py 1000 register`** to register 1000 random users, all the user details are generated using random strings

**`python3 xonotic-sim.py 128 start`**  to start a game lobby with estimated 128 intented users out of the 1000 registered earlier.

**`python3 xonotic-sim.py 64 start`**  to start a game lobby with estimated 64 intented users out of the 1000 registered earlier.

The `start` argument will create a game lobby, register users to the lobby and start a simulated match with random kills over a duration of time up to a certain pre defined randomized total kill number.

Once this is done, we can switch to the web UI to see the data live on the xonotic-ui SG and US clusters.

***Note:** To disalbe automatic VISUAL mode in VIM within GCP, enter `:set mouse-=a` within VIM.*

### Thank you 6m11
