gcloud container clusters get-credentials xonotic-game-us --region=us-central1

kubectl create namespace agones-system

kubectl apply -f https://raw.githubusercontent.com/googleforgames/agones/release-1.16.0/install/yaml/install.yaml

sleep 1m

kubectl get --namespace agones-system pods

gcloud game servers realms create realm-xonotic-us \
--time-zone US/Central \
--location us-central1

gcloud game servers clusters create cluster-xonotic-us \
--realm=realm-xonotic-us \
--gke-cluster locations/us-central1/clusters/xonotic-game-us \
--namespace=default \
--location us-central1 \
--no-dry-run

# gcloud game servers deployments create deployment-xonotic

# gcloud game servers configs create config-1 \
# --deployment deployment-xonotic \
# --fleet-configs-file xonotic_fleet_configs.yaml \
# --scaling-configs-file xonotic_scaling_configs.yaml

gcloud game servers deployments update-rollout deployment-xonotic \
--default-config config-1 --no-dry-run

kubectl get fleet

# gcloud compute firewall-rules create gcgs-xonotic-firewall \
# --network demo-vpc \
# --allow udp:7000-8000 \
# --target-tags game-server \
# --description "Firewall to allow game server udp traffic"

kubectl get gameserver