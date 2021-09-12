export PROJECT_ID=mountkirk-test             # enter GCP Project ID
export SERVICE_ACCOUNT_ID=xonotic-sa         # enter GCP custom service account to use

./xonotic-game.sh
./config-xonotic-game.sh
./xonotic-gameservers.sh
./xonotic-ui.sh
# ~/gcp/patch-sample-ui-yaml/deploy-ui.sh
./app/deploy.sh
