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

Create two files, `deploy.yaml` and `deploy_lb.yaml`

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

### Thank you 6m11