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
3. Build Docker image with: `pack build --builder=heroku/buildpacks:20 --creation-time now registry.code.roche.com/one-d-ai/early-adopters/automated-docker-images/custom-model:1.0.0`

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


### Importing private packages

To install private packages with Poetry and GitLab, you can follow these steps:

1. Make sure you have the necessary access credentials for the private GitLab repository that hosts the package.

2. Open your terminal and navigate to the root directory of your project.

3. Add the private GitLab repository as a dependency source in your `pyproject.toml` file. You can do this by adding the following lines under the `[tool.poetry.dependencies]` section:

   ```toml
   [[tool.poetry.source]]
   name = "my-private-repo"
   url = "https://code.roche.com/api/v4/projects/362083/packages/pypi/simple/"
   priority = "supplemental"
   ```

   Replace `my-private-repo` with a name of your choice and `https://gitlab.com/your-username/your-private-repo.git` with the URL of your private GitLab repository.

4. Save the `pyproject.toml` file.

5. Run the following command to authenticate with GitLab and install the private package:

   ```bash
   poetry config http-basic.my-private-repo __token__ your-PAT-token
   poetry install
   ```

   Replace `my-private-repo` with the name you used in step 3, `your-username` with your GitLab username, and `your-access-token` with a personal access token that has access to the private repository.

   Note: You can generate a personal access token in GitLab by going to your GitLab account settings and navigating to "Access Tokens".

6. Poetry will now fetch and install the private package from the GitLab repository along with any other dependencies specified in your `pyproject.toml` file.

Remember to replace `your-username` and `your-private-repo` with your actual GitLab username and repository URL.
