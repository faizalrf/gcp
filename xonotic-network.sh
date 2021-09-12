gcloud compute networks create demo-vpc --subnet-mode custom

gcloud compute networks subnets create subnet-sg \
--network demo-vpc \
--range "192.168.100.0/24" \
--region asia-southeast1
