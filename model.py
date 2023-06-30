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
# from: https://github.com/kserve/kserve/blob/master/python/sklearnserver/sklearnserver/model.py
import os

import kserve
import joblib
import pathlib
from typing import Dict
import logging
from kserve.errors import InferenceError, ModelMissingError

MODEL_EXTENSIONS = (".joblib", ".pkl", ".pickle")
ENV_PREDICT_PROBA = "PREDICT_PROBA"


class SKLearnModel(kserve.Model):  # pylint:disable=c-extension-no-member
    def __init__(self, name: str, model_dir: str):
        super().__init__(name)
        self.name = name
        self.model_dir = model_dir
        self.ready = False

    def load(self) -> bool:
        model_path = pathlib.Path(kserve.Storage.download(self.model_dir))
        model_files = []
        for file in os.listdir(model_path):
            file_path = os.path.join(model_path, file)
            if os.path.isfile(file_path) and file.endswith(MODEL_EXTENSIONS):
                model_files.append(model_path / file)
        if len(model_files) == 0:
            raise ModelMissingError(model_path)
        elif len(model_files) > 1:
            raise RuntimeError('More than one model file is detected, '
                               f'Only one is allowed within model_dir: {model_files}')
        self._model = joblib.load(model_files[0])
        self.ready = True
        return self.ready

    def predict(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        instances = payload["instances"]
        try:
            if os.environ.get(ENV_PREDICT_PROBA, "false").lower() == "true" and \
                    hasattr(self._model, "predict_proba"):
                result = self._model.predict_proba(instances).tolist()
            else:
                result = self._model.predict(instances).tolist()
            return {"predictions": result}
        except Exception as e:
            raise InferenceError(str(e))
        
if __name__ == "__main__":
    model = SKLearnModel(name = "model", model_dir = "/workspace")
    try:
        model.load()

    except ModelMissingError:
        logging.error(f"fail to locate model file for model {model_name} under dir {model_dir},"
                      f"trying loading from model repository.")

    kserve.ModelServer().start([model])