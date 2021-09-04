export region_name=us-central1
export cluster_name=xonotic-game-us
gcloud container clusters get-credentials $cluster_name --region $region_name
