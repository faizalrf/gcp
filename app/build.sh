Version=$1
if [ "$#" -ne 1 ]; then
    echo "Must specify the version number for the build and deployment"
    echo "build.sh 1"
    echo
    exit 1
fi
# remove all local images
# docker rmi $(docker images -a -q) -f

# remove GCR images
gcloud container images delete gcr.io/group1-6m11/x-leaderboard:v1

kubectl delete -f ./deploy.yaml
kubectl delete -f ./deploy-lb.yaml
docker build -t x-leaderboard:v${Version} .
docker tag x-leaderboard:v${Version} gcr.io/$DEVSHELL_PROJECT_ID/x-leaderboard:v${Version}
docker push gcr.io/$DEVSHELL_PROJECT_ID/x-leaderboard:v${Version}
kubectl apply -f ./deploy.yaml
kubectl apply -f ./deploy-lb.yaml
