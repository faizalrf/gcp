. ~/gcp/config-xonotic-env.sh

Version=$1
if [ "$#" -ne 1 ]; then
    echo "Must specify the version number for the build and deployment"
    echo "deploy.sh 1"
    echo
    exit 1
fi

docker build -t x-leaderboard:v${Version} ~/gcp/app/.
docker tag x-leaderboard:v${Version} gcr.io/$PROJECT_ID/x-leaderboard:v${Version}

# gcloud container clusters get-credentials xonotic-game --region asia-southeast1 --project $PROJECT_ID
docker push gcr.io/$PROJECT_ID/x-leaderboard:v${Version}

# gcloud container clusters get-credentials xonotic-game-us --region us-central1 --project $PROJECT_ID
# docker push gcr.io/$PROJECT_ID/x-leaderboard:v${Version}

kubectl apply -f ~/gcp/app/deploy.yaml
kubectl apply -f ~/gcp/app/deploy-lb.yaml
kubectl apply -f ~/gcp/app/deploy-ingress.yaml

# kubectl autoscale deployment xonotic-ui --max 6 --min 1 --cpu-percent 60
