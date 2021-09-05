export region_name=asia-southeast1
export cluster_name=xonotic-game
gcloud container clusters get-credentials $cluster_name --region $region_name
