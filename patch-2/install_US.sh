export PROJECT_ID=mountkirk-test             # enter GCP Project ID
export SERVICE_ACCOUNT_ID=xonotic-sa         # enter GCP custom service account to use

./xonotic-game_US.sh
./config-xonotic-game_US.sh
./xonotic-gameservers_US.sh
./xonotic-ui_US.sh
# ~/gcp/patch-sample-ui-yaml/deploy-ui.sh
./app/deploy.sh
