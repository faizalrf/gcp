Version=$1
if [ "$#" -ne 1 ]; then
    echo "Must specify the version number for the build and deployment"
    echo "build.sh 1"
    echo
    exit 1
fi
docker build -t x-leaderboard:v${Version} .
docker tag x-leaderboard:v${Version} gcr.io/$DEVSHELL_PROJECT_ID/x-leaderboard:v${Version}
docker push gcr.io/$DEVSHELL_PROJECT_ID/x-leaderboard:v${Version}