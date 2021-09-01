# Mountkirk Game Implementation 6m11

Start by the following two to set the user and project in cloud shell.

```
$ gcloud auth list
$ gcloud config list project
```

To check debug logs of a VM, the following command is handy

```
$ gcloud compute instances tail-serial-port-output template-vm --zone=us-central1-a
```

Here `template-vm` is the VM name, change accordingly.

Set up GKE environment with the following

```
source <(kubectl completion bash)
```

## GKE

### Create Game Cluster

Provided in this repo as `xonotic-game.sh` execute it as `./xonotic-game.sh`

```
$ gcloud beta container --project group1-6m11 clusters create xonotic-game \
--region asia-southeast1 \
--cluster-version 1.20.8-gke.900 \
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

### Create UI Cluster

Provided in this repo as `xonotic-ui.sh` execute it as `./xonotic-ui.sh`

```
$ gcloud beta container --project group1-6m11 clusters create xonotic-ui \
--region asia-southeast1 \
--cluster-version 1.20.8-gke.900 \
--machine-type e2-medium \
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

### Deploy UI App

Once the clusters are ready, we can now deploy the test app

```
$ export region_name=asia-southeast1
$ export cluster_name=xonotic-ui
$ gcloud container clusters get-credentials $cluster_name --region $region_name
```

Two files provided `deploy.yaml` and `deploy_lb.yaml`

`deploy.yaml` should have the following content

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
      - name: hello
        image: "gcr.io/google-samples/hello-app:2.0"
        ports:
        - containerPort: 8080
```

This will deploy the hello-world app to the cluster.

`deploy_lb.yaml` should contain the following. 

```
apiVersion: v1
kind: Service
metadata:
  name: xonotic-ui
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
  selector:
    app: xonotic-ui
```

This will deplopy a HTTP LoadBalancer to connect to the `xonotic-ui` cluster

#### Deployment

To deploy the UI app, `deploy.yaml` and `deploy-lb.yaml`

- `kubectl apply -f ./deploy.yaml`
- `kubectl apply -f ./deploy-lb.yaml`

Check the deployment status and pods / services

```
$ kubectl get deployments
$ kubectl get svc,pods
```

To remove the deployments

- `kubectl delete -f ./deploy.yaml`
- `kubectl delete -f ./deploy-lb.yaml`

## CloudSQL

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
| leaderboard         |
| profile             |
+---------------------+
3 rows in set (0.001 sec)
```

Now the game_user can connect to the CLoudSQL instance from the static IP host, static IP is reqired and is configured under the networking part of the CloudSQL database.

- `profile` table contains details about the player who have Xonotic game account
- `game` table is the current ongoing games and the past games that have ended
- `leaderboard` contains the details of all the games such as
  - When did the player started playing that particular session
  - When did he die in game
  - Which player killed him

The leaderboard table can be used to query a particular game and identify who is the leader or identify the top 10 players in a game or, top 10 players across different game sessions.

```
MySQL [xonoticdb]> desc profile;
+----------------+---------------------+------+-----+----------------------+--------------------------------+
| Field          | Type                | Null | Key | Default              | Extra                          |
+----------------+---------------------+------+-----+----------------------+--------------------------------+
| id             | bigint(20) unsigned | NO   | PRI | NULL                 | auto_increment                 |
| user_name      | varchar(120)        | YES  |     | NULL                 |                                |
| user_email     | varchar(60)         | YES  |     | NULL                 |                                |
| user_equipment | json                | YES  |     | NULL                 |                                |
| user_level     | smallint(6)         | YES  |     | NULL                 |                                |
| ts             | timestamp(6)        | NO   |     | CURRENT_TIMESTAMP(6) | on update CURRENT_TIMESTAMP(6) |
+----------------+---------------------+------+-----+----------------------+--------------------------------+
6 rows in set (0.006 sec)

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

MySQL [xonoticdb]> desc leaderboard;
+---------------+---------------------+------+-----+----------------------+--------------------------------+
| Field         | Type                | Null | Key | Default              | Extra                          |
+---------------+---------------------+------+-----+----------------------+--------------------------------+
| id            | bigint(20) unsigned | NO   | PRI | NULL                 | auto_increment                 |
| game_id       | int(10) unsigned    | NO   |     | NULL                 |                                |
| player_id     | bigint(20)          | NO   |     | NULL                 |                                |
| killed_by     | bigint(20)          | NO   | MUL | NULL                 |                                |
| joined_server | timestamp(6)        | NO   |     | CURRENT_TIMESTAMP(6) |                                |
| ts            | timestamp(6)        | NO   |     | CURRENT_TIMESTAMP(6) | on update CURRENT_TIMESTAMP(6) |
+---------------+---------------------+------+-----+----------------------+--------------------------------+
6 rows in set (0.001 sec)
```

set***Note:** To disalbe automatic VISUAL mode in VIM within GCP, enter `:set mouse-=a` within VIM.*

### Thank you 6m11
