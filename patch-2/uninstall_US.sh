read -p "Are you sure you want to continue delete? <y/N> " prompt
if [[ $prompt == "y" || $prompt == "Y" || $prompt == "yes" || $prompt == "Yes" ]]
then
  # yes | gcloud compute firewall-rules delete gcgs-xonotic-firewall

  # yes | gcloud game servers deployments update-rollout deployment-xonotic \
  # --clear-default-config --no-dry-run

  # yes | gcloud game servers configs delete config-1 \
  # --deployment deployment-xonotic

  # yes | gcloud game servers deployments delete deployment-xonotic

  yes | gcloud game servers realms delete realm-xonotic-us
	
	yes | gcloud container clusters delete xonotic-game-us --region=us-central1
else
  exit 0
fi
