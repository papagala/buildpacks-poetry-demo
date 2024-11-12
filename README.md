# Docker images with buildpacks

This repository is a non-trival example of how to use Cloud Native Buildpacks using the paketo builder. Also, this installed a private package. 

## Prerequisites

1. Install poetry with  `curl -sSL https://install.python-poetry.org | python3 -` or follow the [documentation](https://python-poetry.org/docs/#installing-with-the-official-installer).
2. Install `pack` cli with `brew install buildpacks/tap/pack` or follow the [documentation](https://buildpacks.io/docs/for-platform-operators/how-to/integrate-ci/pack/)
3. You need to have docker installed locally in order to build and run docker images. You can use [Docker Desktop](https://www.docker.com/products/docker-desktop/).

## Buildpacks files

This repository only uses poetry and a special file called `Procfile`.

1. Create `Procfile`, where the entrypoint for docker image will be specified (sample `Procfile` content: `web: python -m model`). See [Procfile format docs](https://devcenter.heroku.com/articles/procfile#procfile-format) for more information.

## Building a new image locally

Make sure you replace your token below where it says `__your_token__`.

```bash
DOCKER_REGISTRY="oswaldodocker/automated-docker-images" \
TAG="0.1.0"

pack build "${DOCKER_REGISTRY}:${TAG}" \
  --builder paketobuildpacks/builder-jammy-base
```

## Testing locally

1. Run docker image created with buildpacks. 

```bash
DOCKER_REGISTRY="oswaldodocker/automated-docker-images" \
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

## Using GitHub actions

Follow instructions [here](https://buildpacks.io/docs/for-buildpack-authors/how-to/distribute-buildpacks/publish-buildpack/with-github-actions/).

## Advanced

### Caching

You can make use of caching so that CI/CD will take much less than than without it.

```bash
pack build oswaldodocker/automated-docker-images:0.1.0 \
  --builder paketobuildpacks/builder-jammy-base \
  --cache-image oswaldodocker/automated-docker-images:cache-image \
  --publish \
  --volume "$PWD/bindings:/usr/local/share/ca-certificates/"
```

### CA-Certificates

You can add run-time ca-certificates during buildtime so that they are available during run time

```bash
pack build oswaldodocker/automated-docker-images:0.1.0 \
  --builder paketobuildpacks/builder-jammy-base \
  --cache-image oswaldodocker/automated-docker-images:cache-image \
  --publish \
  --volume "$PWD/bindings:/usr/local/share/ca-certificates/"
```

In Kubernetes there are different ways to deal with this as well like deploying an Ingress Controller and adding the corporate certificates there if needed, do it via Istio or store the certificates in the cluster and mount it to the deployment directly.