. ~/gcp/config-xonotic-env.sh

docker build -t x-leaderboard:v1 ~/gcp/app/.
docker tag x-leaderboard:v1 gcr.io/$PROJECT_ID/x-leaderboard:v1

docker push gcr.io/$PROJECT_ID/x-leaderboard:v1

kubectl apply -f ~/gcp/app/deploy.yaml
kubectl apply -f ~/gcp/app/deploy-lb.yaml
kubectl apply -f ~/gcp/app/deploy-ingress.yaml

# kubectl autoscale deployment xonotic-ui --max 6 --min 1 --cpu-percent 60
