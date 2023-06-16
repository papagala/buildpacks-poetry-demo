# automated-docker-images

# Prerequisites
Install pack CLI, according to the manual: https://buildpacks.io/docs/tools/pack/


# Log
1) prepared enviorment using poetry
2)trained sklearn model (train_model.py)
3) get model.py from kserve github
4) copied poetry lock into requirements.txt (`poetry export --without-hashes --format=requirements.txt > requirements.txt`)
5) run `pack build --builder=heroku/buildpacks:20 registry.code.roche.com/one-d-ai/early-adopters/automated-docker-images/custom-model:v1` to build dokcer image
6) tested docker image locally 

