# Docker images with buildpacks

This repository is a non-trival example of how to use Cloud Native Buildpacks using the paketo builder. Also, this installed a private package. 

## Prerequisites

1. Install poetry with  `curl -sSL https://install.python-poetry.org | python3 -` or follow the [documentation](https://python-poetry.org/docs/#installing-with-the-official-installer).
2. Install `pack` cli with `brew install buildpacks/tap/pack` or follow the [documentation](https://buildpacks.io/docs/for-platform-operators/how-to/integrate-ci/pack/)
3. You need to have docker installed locally in order to build and run docker images. You can use [Docker Desktop](https://www.docker.com/products/docker-desktop/). Make sure you request Docker Business subscription [info](https://devhub.roche.com/catalog/default/system/fk-ef-docker-business).

## Buildpacks files

This repository only uses poetry and a special file called `Procfile`.

1. Create `Procfile`, where the entrypoint for docker image will be specified (sample `Procfile` content: `web: python -m model`). See [Procfile format docs](https://devcenter.heroku.com/articles/procfile#procfile-format) for more information.

## Building a new image locally

Make sure you replace your token below where it says `__your_token__`.

```bash
CI_API_V4_URL="https://code.roche.com/api/v4" \
PROJECT_ID="362083" \
DOCKER_REGISTRY="registry.code.roche.com/gomezmj2/automated-docker-images" \
TAG="0.1.0"

pack build "${DOCKER_REGISTRY}:${TAG}" \
  --builder paketobuildpacks/builder-jammy-base \
  --env POETRY_HTTP_BASIC_FOO_USERNAME=___token__ \
  --env POETRY_HTTP_BASIC_FOO_PASSWORD=__your_token__ \
  --env POETRY_REPOSITORIES_FOO_URL="${CI_API_V4_URL}/projects/${PROJECT_ID}/packages/pypi/simple/"
```

## Testing locally

1. Run docker image created with buildpacks. 

```bash
DOCKER_REGISTRY="registry.code.roche.com/gomezmj2/automated-docker-images" \
TAG="0.1.0"

docker run -ePORT=8080 -p8080:8080 "${DOCKER_REGISTRY}:${TAG}"
```

From another terminal run:

```bash
curl --location --request POST 'localhost:8080/v1/models/model:predict' \
  --header 'Content-Type: application/json' \
  --data-raw '{"instances": [[6.8, 2.8, 4.8, 1.4],[6.0, 3.4, 4.5, 1.6]]}'
```

Expected response:

```bash
{"predictions":[1,1]}
```

## Using GitLab CI

This repository has an example `.gitlab-ci.yml` that installs `pack` CLI, builds a docker image and even builds a cache image so that upcoming CI/CD runs become faster since `poetry` will not try to resolve dependencies again, nor reinstall any packages. 

Currently this repositories version will be used as a tag of the docker image, if you make some changes, make sure you run 

```bash
poetry versin patch 
```

And commit your changes in a new branch, and open up a Merge Request. 

## Importing private packages

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

You can also go to the private GitLab that hosts the private package that you want to install, and go to Settings > CI/CD > Token Access and click on `Add project` so that you can use the `$CI_JOB_TOKEN` environment variable that is always present during any CI/CD in GitLab to authenticate like in the .gitlab-ci.yml in this repository. 

```yaml
pack build
"${CI_REGISTRY_IMAGE}:${PACKAGE_VERSION}"
--builder paketobuildpacks/builder-jammy-base
--cache-image "${CI_REGISTRY_IMAGE}:${CACHE_IMAGE_NAME}"
--publish
--env 'BP_CPYTHON_VERSION=3.10.*'
--env POETRY_HTTP_BASIC_FOO_USERNAME=gitlab-ci-token
--env POETRY_HTTP_BASIC_FOO_PASSWORD=$CI_JOB_TOKEN
--env POETRY_REPOSITORIES_FOO_URL=${CI_API_V4_URL}/projects/362083/packages/pypi/simple/
```

## Advanced

### Caching

You can make use of caching so that GitLab CI/CD will take much less than than without it.

```bash
pack build registry.code.roche.com/gomezmj2/automated-docker-images:0.1.0 \
  --builder paketobuildpacks/builder-jammy-base \
  --env POETRY_HTTP_BASIC_FOO_USERNAME=___token__ \
  --env POETRY_HTTP_BASIC_FOO_PASSWORD=__your_token__ \
  --env POETRY_REPOSITORIES_FOO_URL=https://code.roche.com/api/v4/projects/362083/packages/pypi/simple/ \
  --env SERVICE_BINDING_ROOT=/usr/local/share/ca-certificates/ \
  --env BP_EMBED_CERTS=true \
  --cache-image registry.code.roche.com/gomezmj2/automated-docker-images:cache-image \
  --publish \
  --volume "$PWD/bindings:/usr/local/share/ca-certificates/"
```

### CA-Certificates

You can add run-time ca-certificates during buildtime so that they are available during run time

```bash
pack build registry.code.roche.com/gomezmj2/automated-docker-images:0.1.0 \
  --builder paketobuildpacks/builder-jammy-base \
  --env POETRY_HTTP_BASIC_FOO_USERNAME=___token__ \
  --env POETRY_HTTP_BASIC_FOO_PASSWORD=__your_token__ \
  --env POETRY_REPOSITORIES_FOO_URL=https://code.roche.com/api/v4/projects/362083/packages/pypi/simple/ \
  --env SERVICE_BINDING_ROOT=/usr/local/share/ca-certificates/ \
  --env BP_EMBED_CERTS=true \
  --cache-image registry.code.roche.com/gomezmj2/automated-docker-images:cache-image \
  --publish \
  --volume "$PWD/bindings:/usr/local/share/ca-certificates/"
```

If you rather worry about adding ca-certificates during run time, and you are deploying this in Kubernetes, checkout the project [Roche Certs Kubernetes Volume](https://code.roche.com/librarians/developer-experience/roche-certs-kubernetes-volume#using-with-paketo-built-images). Thanks Cezary Krzyzanowski for sharing this with me. 