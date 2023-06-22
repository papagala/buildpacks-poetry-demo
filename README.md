# automated-docker-images



## Instructions 
### Prerequisites:
1) Created pyproject.toml file to handle packages via poetry and run poetry (`poetry build`) to create enviorment. 
2) Trained sklearn model using train_model.py, model.joblib was created
3) Create functions that will load the model and run prediction (model.py) - code was copied from: https://github.com/kserve/kserve/blob/master/python/sklearnserver/sklearnserver/model.py 
### Running the buildpacks: 
4) Install pack CLI, according to the manual: https://buildpacks.io/docs/tools/pack/
5) Create Procfile, where entrypoint for docker image will be specified
6) Create runtime.txt where version of python will be specified 
7) Copy poetry.lock into requierments.txt, used by buildpacks (`poetry export --without-hashes --format=requirements.txt > requirements.txt`)
8) run `pack build --builder=heroku/buildpacks:20 registry.code.roche.com/one-d-ai/early-adopters/automated-docker-images/custom-model:v1` to build docker image
### Testing locally:
9) Run docker created by bulidpack: `docker run -ePORT=8080 -p8080:8080 registry.code.roche.com/one-d-ai/early-adopters/automated-docker-images/custom-model:v1` and check if it can be queried: `curl localhost:8080/v1/models/model:predict -d @./input.json`
### Testing on uat: 
10) Push docker image to registry: `docker push registry.code.roche.com/one-d-ai/early-adopters/automated-docker-images/custom-model:v1`
11) deploy manually to the UAT cluster (MLPP namespace) using `kubectl apply -f kserve-deployment.yaml -n mlpp`. Make sure that this namespace have access to imagePullSecret, that store gitlab deploy token, so it can pull the image needed (compare with this MR: https://code.roche.com/one-d-ai/platform/projects-control-plane/-/merge_requests/54). 
12) After that check if inference service can be accessed, e.g. by 
`curl --location --request POST  'https://ea-custom-model-predictor-default.mlpp.inference.kubeflow.dev.pred-mlops.roche.com/v1/models/model:predict' \
--header 'Cookie: authservice_session=COOKIE' \
--header 'Content-Type: application/json' \
--data-raw '{"instances": [[6.8, 2.8, 4.8, 1.4],[6.0, 3.4, 4.5, 1.6]]}'` where COOKIE stands for value of cookie for kubeflow session. 
