# Automated Docker images

This example is used for the automatic Docker image creation of the sklearn framework with a [public sklearn model](https://kserve.github.io/website/0.8/modelserving/v1beta1/sklearn/v2/).

## Usage

### Prerequisites

1. Create `pyproject.toml` file to handle packages via poetry
2. Run poetry (`poetry build`) to create the environment
3. Train sklearn model using `train_model.py`, which will output the `model.joblib` file
4. Create functions that will load the model and run prediction (`model.py`) - the code was copied from: [https://github.com/kserve/kserve/blob/master/python/sklearnserver/sklearnserver/model.py](https://github.com/kserve/kserve/blob/master/python/sklearnserver/sklearnserver/model.py)

### Running buildpacks

1. Install pack CLI, according to the manual: [https://buildpacks.io/docs/tools/pack/](https://buildpacks.io/docs/tools/pack/)
2. Create `Procfile`, where the entrypoint for docker image will be specified (sample `Procfile` content: `web: python -m model`). See [Procfile format docs](https://devcenter.heroku.com/articles/procfile#procfile-format) for more information.
3. Create `runtime.txt` where Python version will be specified (e.g.: `python-3.8.17`)
4. Export `poetry.lock` into `requierments.txt`, used by buildpacks, with: `poetry export --without-hashes --format=requirements.txt > requirements.txt`
5. Build Docker image with: `pack build --builder=heroku/buildpacks:20 --creation-time now registry.code.roche.com/one-d-ai/early-adopters/automated-docker-images/custom-model:1.0.0`

## Testing

### Testing locally

1. Run Docker created by bulidpacks: `docker run -ePORT=8080 -p8080:8080 registry.code.roche.com/one-d-ai/early-adopters/automated-docker-images/custom-model:1.0.0`
2. Check if it can be queried: `curl localhost:8080/v1/models/model:predict -d @./input.json`

### Testing on dev

1. Push Docker image into the GitLab container registry: `docker push registry.code.roche.com/one-d-ai/early-adopters/automated-docker-images/custom-model:1.0.0`
2. Deploy manually to the DEV cluster (`mlpp` namespace) using `kubectl apply -f kserve-deployment.yaml -n mlpp`. Make sure that this namespace has access to the imagePullSecret, which stores the GitLab deploy token, so that it can pull the required image (compare with this MR: [https://code.roche.com/one-d-ai/platform/projects-control-plane/-/merge_requests/54](https://code.roche.com/one-d-ai/platform/projects-control-plane/-/merge_requests/54))
3. Obtain the [Kubeflow Dev](https://dashboard.kubeflow.dev.pred-mlops.roche.com/) session cookie to authenticate with the endpoint
   - In Chrome, you need to open the "Developer Tools" menu (e.g by right clicking anywhere on [the Kubeflow page](https://dashboard.kubeflow.dev.pred-mlops.roche.com/) and selecting the `Inspect` option from the context menu), now you can go to the `Application` tab, and in the left hand-side `Storage` section under `Cookies` select the `https://dashboard.kubeflow.dev.pred-mlops.roche.com/` cookie and copy the string value of `authservice_session`
4. Afterwards, check if the inference service can be accessed. e.g. with this `curl` command (make sure to replace the `COOKIE` with the value from the previous step):

    ```bash
    curl --location --request POST  'https://ea-custom-model-predictor-default.mlpp.inference.kubeflow.dev.pred-mlops.roche.com/v1/models/model:predict' \
    --header 'Cookie: authservice_session=COOKIE' \
    --header 'Content-Type: application/json' \
    --data-raw '{"instances": [[6.8, 2.8, 4.8, 1.4],[6.0, 3.4, 4.5, 1.6]]}'
    ```

    In the output, you should receive:

    ```bash
    {"predictions":[1,1]}
    ```
