. ../config-xonotic-env.sh

gcloud container --project $PROJECT_ID node-pools create xonotic-ui-pool \
--cluster xonotic-game-us \
--region us-central1 \
--tags=game-ui \
--machine-type n1-standard-1 \
--image-type "COS_CONTAINERD" \
--disk-type "pd-standard" --disk-size 100 \
--service-account "$SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
--num-nodes 1 \
--enable-autoscaling --min-nodes 1 --max-nodes 3 \
--no-enable-autoupgrade \
--enable-autorepair \
--max-surge-upgrade 1 \
--max-unavailable-upgrade 0 \
--shielded-secure-boot --shielded-integrity-monitoring \
--node-labels=pool=xonotic-ui-pool \
--node-locations "us-central1-a"
#,"us-central1-b","us-central1-c"
