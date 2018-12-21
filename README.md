# Rekcurd

[![Build Status](https://travis-ci.com/rekcurd/drucker.svg?branch=master)](https://travis-ci.com/rekcurd/drucker)
[![PyPI version](https://badge.fury.io/py/rekcurd.svg)](https://badge.fury.io/py/rekcurd)
[![codecov](https://codecov.io/gh/rekcurd/drucker/branch/master/graph/badge.svg)](https://codecov.io/gh/rekcurd/drucker "Non-generated packages only")
[![pypi supported versions](https://img.shields.io/pypi/pyversions/rekcurd.svg)](https://pypi.python.org/pypi/rekcurd)

Rekcurd is the Project for serving ML module. This is a gRPC micro-framework and it can be used like [Flask](http://flask.pocoo.org/). 


## Parent Project
https://github.com/rekcurd/drucker-parent


## Components
- [Rekcurd](https://github.com/rekcurd/drucker) (here): Project for serving ML module.
- [Rekcurd-dashboard](https://github.com/rekcurd/drucker-dashboard): Project for managing ML model and deploying ML module.
- [Rekcurd-client](https://github.com/rekcurd/drucker-client): Project for integrating ML module. 


## Installation
From source:

```bash
$ git clone --recursive https://github.com/rekcurd/drucker.git
$ cd drucker
$ python setup.py install
```

From [PyPi](https://pypi.org/project/rekcurd/) directly:

```bash
$ pip install rekcurd
```

## How to use
Example code is available [here](https://github.com/rekcurd/drucker-example).

### settings.yml
This is the configuration file of your ML module. Template is available [here](./template/settings.yml).

```yaml
# Debug flag
test: True

# This must be unique.
# It can be overwritten with the environment variable "DRUCKER_APPLICATION_NAME".
app.name: drucker-sample

# It can be overwritten with the environment variable "DRUCKER_SERVICE_PORT".
app.port: 5000

# This must be unique.
# It can be overwritten with the environment variable "DRUCKER_SERVICE_NAME".
app.service.name: dev-001

# This must be one of [development/beta/staging/sandbox/production].
# It can be overwritten with the environment variable "DRUCKER_SERVICE_LEVEL".
app.service.level: development

# ML model
# Put your model file under "{app.modeldir}/{app.name}/{app.modelfile}".
# If you use Drucker-dashboard, {app.modelfile} is set automatically.
# If you setup MySQL server, {app.modelfile} is set automatically.
#   Model directory:  DRUCKER_SERVICE_MODEL_DIR > app.modeldir
#   Model filepath:   DB entry > DRUCKER_SERVICE_MODEL_FILE > app.modelfile
app.modeldir: ./model
app.modelfile: default.model

# DB
# "use.db" must be one of [sqlite(default)/mysql].
# If you use Drucker-dashboard, these values are set automatically.
#   DB type: DRUCKER_DB_MODE > use.db
#   MySQL host: DRUCKER_DB_MYSQL_HOST > db.mysql.host
#   MySQL port: DRUCKER_DB_MYSQL_PORT > db.mysql.port
#   MySQL DB name: DRUCKER_DB_MYSQL_DBNAME > db.mysql.dbname
#   MySQL user: DRUCKER_DB_MYSQL_USER > db.mysql.user
#   MySQL password: DRUCKER_DB_MYSQL_PASSWORD > db.mysql.password
use.db: sqlite
db.mysql.host: localhost
db.mysql.port: 3306
db.mysql.dbname: assignment
db.mysql.user: user
db.mysql.password: pass
```

### app.py
This is the Rekcurdized application of your ML module. Example code is available [here](./template/app.py).

```python
import traceback
import csv
import os
import io

from typing import Tuple, List

from drucker.logger import JsonSystemLogger
from drucker import Drucker
from drucker.utils import PredictLabel, PredictResult, EvaluateResult, EvaluateDetail

import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.externals import joblib
import zipfile


def joblib_load_from_zip(zip_name: str, file_name: str):
    with zipfile.ZipFile(zip_name, 'r') as zf:
        with zf.open(file_name, 'r') as zipmodel:
            return joblib.load(io.BufferedReader(io.BytesIO(zipmodel.read())))


class MyApp(Drucker):
    def __init__(self, config_file: str = None):
        super().__init__(config_file)
        self.logger = JsonSystemLogger(self.config)
        self.load_model()

    def load_model(self) -> None:
        assert self.model_path is not None, \
            'Please specify your ML model path'
        try:
            self.predictor = joblib.load(self.model_path)
            # file_name = 'default.model'
            # self.predictor = joblib_load_from_zip(self.model_path, file_name)

        except Exception as e:
            self.logger.error(str(e))
            self.logger.error(traceback.format_exc())
            self.predictor = None
            if not self.is_first_boot():
                os._exit(-1)

    def predict(self, input: PredictLabel, option: dict = None) -> PredictResult:
        try:
            label_predict = self.predictor.predict(
                np.array([input], dtype='float64')).tolist()
            return PredictResult(label_predict, [1] * len(label_predict), option={})
        except Exception as e:
            self.logger.error(str(e))
            self.logger.error(traceback.format_exc())
            raise e

    def evaluate(self, file_path: str) -> Tuple[EvaluateResult, List[EvaluateDetail]]:
        try:
            num = 0
            label_gold = []
            label_predict = []
            details = []
            with open(file_path, 'r') as f:
                reader = csv.reader(f, delimiter=",")
                for row in reader:
                    num += 1
                    correct_label = int(row[0])
                    label_gold.append(correct_label)
                    result = self.predict(row[1:], option={})
                    is_correct = correct_label == int(result.label[0])
                    details.append(EvaluateDetail(result, is_correct))
                    label_predict.append(result.label)

            accuracy = accuracy_score(label_gold, label_predict)
            p_r_f = precision_recall_fscore_support(label_gold, label_predict)
            res = EvaluateResult(num, accuracy, p_r_f[0].tolist(), p_r_f[1].tolist(), p_r_f[2].tolist(), {})
            return res, details
        except Exception as e:
            self.logger.error(str(e))
            self.logger.error(traceback.format_exc())
            return EvaluateResult(), []
```

#### load_model method
Implement your ML model loading method.

```python
def load_model(self) -> None:
    try:
        self.predictor = joblib.load(self.model_path)
    except Exception as e:
        self.logger.error(str(e))
```

If your ML module uses more than two files, you need to create a compressed file which includes the files it requires. And implement the method like the below.

```python
def joblib_load_from_zip(self, zip_name: str, file_name: str):
    with zipfile.ZipFile(zip_name, 'r') as zf:
        with zf.open(file_name, 'r') as zipmodel:
            return joblib.load(io.BufferedReader(io.BytesIO(zipmodel.read())))

def load_model(self) -> None:
    try:
        file_name = 'default.model'
        self.predictor = self.joblib_load_from_zip(self.model_path, file_name)
    except Exception as e:
        self.logger.error(str(e))
```

#### predict method
Implement your ML model predicting/inferring method.

```python
def predict(self, input: PredictLabel, option: dict = None) -> PredictResult:
    try:
        label_predict = self.predictor.predict(
            np.array([input], dtype='float64')).tolist()
        return PredictResult(label_predict, [1] * len(label_predict), option={})
    except Exception as e:
        raise e
```

##### PredictLabel
*V* is the length of feature vector.

|Field |Type |Description |
|:---|:---|:---|
|input <BR>(required) |One of below<BR>- string<BR>- bytes<BR>- string[*V*]<BR>- int[*V*]<BR>- double[*V*] |Input data for inference.<BR>- "Nice weather." for a sentiment analysis.<BR>- PNG file for an image transformation.<BR>- ["a", "b"] for a text summarization.<BR>- [1, 2] for a sales forcast.<BR>- [0.9, 0.1] for mnist data. |
|option |string| Option field. Must be json format. |

The "option" field needs to be a json format. Any style is Ok but we have some reserved fields below.

|Field |Type |Description |
|:---|:---|:---|
|suppress_log_input |bool |True: NOT print the input and output to the log message. <BR>False (default): Print the input and outpu to the log message. |
|YOUR KEY |any |YOUR VALUE |

##### PredictResult
*M* is the number of classes. If your algorithm is a binary classifier, you set *M* to 1. If your algorithm is a multi-class classifier, you set *M* to the number of classes.

|Field |Type |Description |
|:---|:---|:---|
|label<BR>(required) |One of below<BR> -string<BR> -bytes<BR> -string[*M*]<BR> -int[*M*]<BR> -double[*M*] |Result of inference.<BR> -"positive" for a sentiment analysis.<BR> -PNG file for an image transformation.<BR> -["a", "b"] for a multi-class classification.<BR> -[1, 2] for a multi-class classification.<BR> -[0.9, 0.1] for a multi-class classification. |
|score<BR>(required) |One of below<BR> -double<BR> -double[*M*] |Score of result.<BR> -0.98 for a binary classification.<BR> -[0.9, 0.1] for a multi-class classification. |
|option |string |Option field. Must be json format. |

#### evaluate method
Implement your ML model evaluating method.

```python
def evaluate(self, file_path: str) -> Tuple[EvaluateResult, List[EvaluateDetail]]:
    try:
        num = 0
        label_gold = []
        label_predict = []
        details = []
        with open(file_path, 'r') as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                num += 1
                correct_label = int(row[0])
                label_gold.append(correct_label)
                result = self.predict(row[1:], option={})
                is_correct = correct_label == int(result.label[0])
                details.append(EvaluateDetail(result, is_correct))
                label_predict.append(result.label)

        accuracy = accuracy_score(label_gold, label_predict)
        p_r_f = precision_recall_fscore_support(label_gold, label_predict)
        res = EvaluateResult(num, accuracy, p_r_f[0].tolist(), p_r_f[1].tolist(), p_r_f[2].tolist(), {})
        return res, details
    except Exception as e:
        return EvaluateResult(), []
```

##### Input
Input is the file path of your evaluation data. The format is your favorite.

##### EvaluateResult and EvaluateDetail
`EvaluateDetail` is the details of evaluation result.

|Field |Type |Description |
|:---|:---|:---|
|result<BR>(required) |PredictResult |Prediction result. |
|is_correct<BR>(required) |bool |Correct or not. |

`EvaluateResult` is the evaluation score. *N* is the number of evaluation data. *M* is the number of classes. If your algorithm is a binary classifier, you set *M* to 1. If your algorithm is a multi-class classifier, you set *M* to the number of classes.

|Field |Type |Description |
|:---|:---|:---|
|num<BR>(required)|int |Number of evaluation data. |
|accuracy<BR>(required) |double |Accuracy. |
|precision<BR>(required) |double[*N*][*M*] |Precision. |
|recall<BR>(required) |double[*N*][*M*] |Recall. |
|fvalue<BR>(required) |double[*N*][*M*] |F1 value. |

### server.py
This is the gRPC server boot script. Example code is available [here](./template/server.py).

```python
import sys
import os
import pathlib


root_path = pathlib.Path(os.path.abspath(__file__)).parent.parent
sys.path.append(str(root_path))


from concurrent import futures
import grpc
import time

from drucker import DruckerDashboardServicer, DruckerWorkerServicer
from drucker.logger import JsonSystemLogger, JsonServiceLogger
from drucker.protobuf import drucker_pb2_grpc
from app import MyApp

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def serve():
    app = MyApp("./settings.yml")
    system_logger = JsonSystemLogger(app.config)
    service_logger = JsonServiceLogger(app.config)
    system_logger.info("Wake-up drucker worker.")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    drucker_pb2_grpc.add_DruckerDashboardServicer_to_server(
        DruckerDashboardServicer(logger=system_logger, app=app), server)
    drucker_pb2_grpc.add_DruckerWorkerServicer_to_server(
        DruckerWorkerServicer(logger=service_logger, app=app), server)
    server.add_insecure_port("[::]:{0}".format(app.config.SERVICE_PORT))
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        system_logger.info("Shutdown drucker worker.")
        server.stop(0)


if __name__ == '__main__':
    serve()
```

### start.sh
This is the boot script of your ML application. Example code is available [here](./template/start.sh).

```bash
ECHO_PREFIX="[drucker example]: "

set -e
set -u

echo "$ECHO_PREFIX Start.."

pip install -r requirements.txt
python server.py
```

### logger.py (if necessary)
If you want to customize the logger, implement the interface class of [logger_interface.py](./drucker/logger/logger_interface.py)

## Run it!
```
$ sh start.sh
```

## Unittest
```
$ python -m unittest
```

## Kubernetes support
Rekcurd can be run on Kubernetes. See [here](https://github.com/rekcurd/drucker-parent).
