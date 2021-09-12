gcloud compute networks create demo-vpc --subnet-mode custom

gcloud compute networks subnets create subnet-sg \
--network demo-vpc \
--range "192.168.100.0/24" \
--region asia-southeast1

gcloud compute networks subnets create subnet-us \
--network demo-vpc \
--range "192.168.200.0/24" \
--region us-central1

. ./config-xonotic-env.sh

gcloud iam service-accounts create $SERVICE_ACCOUNT_ID

gcloud projects add-iam-policy-binding $PROJECT_ID \
--member="serviceAccount:$SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
--role="roles/viewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
--member="serviceAccount:$SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
--role="roles/gameservices.viewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
--member="serviceAccount:$SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
--role="roles/cloudbuild.serviceAgent"
