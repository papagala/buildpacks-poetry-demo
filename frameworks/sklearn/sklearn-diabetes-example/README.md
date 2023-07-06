# Running an inference endpoint locally

This repository under `frameworks/sklearn/sklearn-diabetes-example/` is a copy of Elina Koletou's repository on <https://code.roche.com/one-d-ai/early-adopters/sklearn-diabetes-example>.

I made an effort to minimize the code from Elina, which turned into adding the following files/dependencies to the root of the repository:

- `Procfile`: This file is in charge of providing the commands that need to run in order to start a KServe endpoint locally.
- `runtime.txt`: Here is where you provide the exact version of Python that will be used (e.g.: `python-3.8.17`).
- `start_inference_endpoint.py`: Is the file that inherits from `kserve.Model` and contains the boilerplate code for starting an inference endpoint.
- Ran `poetry add kserve="^0.10.2"` so that we can start creating an inference endpoint. This adds the right dependencies to the `pyproject.toml` file.
  - `requirements.txt`: Created by running `poetry export --without-hashes --without dev -f requirements.txt -o requirements.txt`.
- Built the Docker image with `pack build --builder=heroku/buildpacks:20 --creation-time now registry.code.roche.com/one-d-ai/early-adopters/automated-docker-images/diabetes:1.0.0`. In order to run this command, you must install [pack](https://buildpacks.io/docs/tools/pack/#install).
- kserve-deployment.yaml: This is an example file that maps the built image above, into a Kubernetes `apiVersion: serving.kserve.io/v1beta1`.

## Locally spin up an endpoint

### First we need to create a docker using build packs. First install `brew`

## Usage

### Requirements

- [pack](https://buildpacks.io/docs/tools/pack/) - on macOS you can install it with [brew](https://brew.sh/), using: `brew install buildpacks/tap/pack`
- [poetry](https://python-poetry.org/docs/) - you can usually install it with: `curl -sSL https://install.python-poetry.org | python3 -`
- [Docker](https://docs.docker.com/engine/install/) - depending on your platform, simply follow [this link](https://docs.docker.com/engine/install/) to install Docker. You could then run the following command to see what Docker containers are running: `docker ps`

### Spin up an endpoint locally

1. Go to the right directory. From your root folder, run:

    ```bash
    cd frameworks/sklearn/sklearn-diabetes-example
    ```

1. Export the `requirements.txt` by running:

    ```bash
    poetry export --without-hashes --without dev -f requirements.txt -o requirements.txt
    ```

1. Build the docker image. From your terminal run:

    ```bash
    image_name=registry.code.roche.com/one-d-ai/early-adopters/automated-docker-images/diabetes:1.0.0
    pack build --builder=heroku/buildpacks:20 --creation-time now $image_name
    ```

1. Run the Docker image locally:

    ```bash
    docker run -ePORT=8080 -p8080:8080 registry.code.roche.com/one-d-ai/early-adopters/automated-docker-images/diabetes:1.0.0
    ```

1. Call your local endpoint to return predictions:

    ```bash
    curl --location 'http://localhost:8080/v1/models/sklearn-diabetes:predict' \
    --header 'Content-Type: application/json' \
    --data '{
        "instances": [
            [
                0.038075906433423026,
                0.05068011873981862,
                0.061696206518683294,
                0.0218723855140367,
                -0.04422349842444599,
                -0.03482076283769895,
                -0.04340084565202491,
                -0.002592261998183278,
                0.019907486170462722,
                -0.01764612515980379
            ],
            [
                -0.0018820165277906047,
                -0.044641636506989144,
                -0.051474061238800654,
                -0.02632752814785296,
                -0.008448724111216851,
                -0.019163339748222204,
                0.07441156407875721,
                -0.03949338287409329,
                -0.0683315470939731,
                -0.092204049626824
            ]
        ]
    }'
    ```

### Notebooks

You may run the `notebooks/` in the following order to train, test locally, and call the local endpoint:

- `01-train-model-locally`
- `02-use-local-model`
- `03-call-local-endpoint`

