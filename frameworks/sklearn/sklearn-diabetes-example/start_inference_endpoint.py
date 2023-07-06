# Copyright 2021 The KServe Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# from:
# https://github.com/kserve/kserve/blob/master/python/sklearnserver/sklearnserver/model.py

import argparse
import logging
import os
import pathlib
from typing import Dict, Optional

import joblib
import kserve
from kserve.errors import InferenceError, ModelMissingError

MODEL_EXTENSIONS = (".joblib", ".pkl", ".pickle")
ENV_PREDICT_PROBA = "PREDICT_PROBA"


class SKLearnModel(kserve.Model):  # pylint:disable=c-extension-no-member
    """Inheriting from KServe Model Public Interface

    Model is intended to be subclassed by various components within KServe.
    """

    def __init__(self, name: str, model_dir: str):
        """Initialization of the model

        Args:
            name (str): Name of the model.
            model_dir (str): Directory where the model `.joblib` is stored.
        """
        super().__init__(name)
        self.name = name
        self.model_dir = model_dir
        self.ready = False

    def load(self) -> bool:
        """Loading of the model from the directory specified.

        Raises:
            ModelMissingError: If there is no model inside the specified folder.
            RuntimeError: If more than one model is inside the specified folder.

        Returns:
            bool: _description_
        """
        model_path = pathlib.Path(kserve.Storage.download(self.model_dir))
        model_files = []
        for file in os.listdir(model_path):
            file_path = os.path.join(model_path, file)
            if os.path.isfile(file_path) and file.endswith(MODEL_EXTENSIONS):
                model_files.append(model_path / file)
        if len(model_files) == 0:
            raise ModelMissingError(model_path)
        elif len(model_files) > 1:
            raise RuntimeError(
                "More than one model file is detected, "
                f"Only one is allowed within model_dir: {model_files}"
            )
        self._model = joblib.load(model_files[0])
        self.ready = True
        return self.ready

    def predict(self, payload: Dict, headers: Optional[Dict[str, str]] = None) -> Dict:
        """Prediction method for ML predictions.

        Args:
            payload (Dict): This is controlled by KServe and it expects
            a very particualr payload. It must be sent as a dictioanry with
            a key called `instances`. The value of `instances` must be
            a list of lists. Each one of the lists inside, is a list with all
            the features that we want a prediction upon.

            Example:

            {
            "instances": [
            [0.038075906433423026,
            0.05068011873981862,
            0.061696206518683294,
            0.0218723855140367,
            -0.04422349842444599,
            -0.03482076283769895,
            -0.04340084565202491,
            -0.002592261998183278,
            0.019907486170462722,
            -0.01764612515980379]
            ]
            }


        Raises:
            InferenceError: Whenever there is an error during prediction

        Returns:
            Dict: a dicionary with `predictions` as key. The value is a
            list with the predictions as a floating point value.

        Example:

        {
            "predictions": [
             204.1345201689273
        ]
        }
        """
        instances = payload["instances"]
        try:
            if os.environ.get(ENV_PREDICT_PROBA, "false").lower() == "true" and hasattr(
                self._model, "predict_proba"
            ):
                result = self._model.predict_proba(instances).tolist()
            else:
                result = self._model.predict(instances).tolist()
            return {"predictions": result}
        except Exception as e:
            raise InferenceError(str(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="model")
    parser.add_argument("--trained_model_path", type=str)
    args = parser.parse_args()

    model_name = f"{args.model_name}"
    model_dir = f"/workspace/{args.trained_model_path}"

    model = SKLearnModel(name=model_name, model_dir=model_dir)

    try:
        model.load()

    except ModelMissingError:
        logging.error(
            f"fail to locate model file for model under dir {model_dir},"
            f"trying loading from model repository named {model_name}."
        )

    kserve.ModelServer().start([model])
